# LPG Cylinder QR/RFID Verification API Documentation

## Overview

This API provides comprehensive cylinder tracking and authenticity verification using QR codes and RFID tags. It implements enterprise-level security measures including:

- **Cryptographic Authentication**: SHA-256 hashing with secret keys
- **Tamper Detection**: Automated detection through scan pattern analysis
- **Complete History Tracking**: Every cylinder interaction is logged
- **Suspicious Activity Detection**: Real-time monitoring for cloning attempts
- **GPS Location Tracking**: Track cylinder movements
- **Role-Based Access Control**: Secure access based on user roles

## Base URL

```
http://localhost:8000/api/
```

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Security Features

### 1. QR/RFID Code Generation
- Unique UUID-based codes for each cylinder
- Automatically generated on registration
- Cannot be modified after creation

### 2. Authentication Hash
- SHA-256 hash combining serial number, QR code, RFID tag, and secret key
- Used for verification and token generation
- Secret key stored securely, never exposed in API responses

### 3. Tamper Detection
- Multiple rapid scans flagged as suspicious (>5 in 5 minutes)
- Impossible location changes detected
- Manual tamper flags with detailed notes
- All suspicious activity logged for security audit

### 4. Audit Trail
- Every scan logged with timestamp, location, and user
- Complete history of all cylinder events
- IP address and user agent captured for security

## API Endpoints

### 1. Register New Cylinder

**Endpoint:** `POST /cylinders/register/`

**Description:** Register a new LPG cylinder with automatically generated QR and RFID codes.

**Permissions:** Dispatcher, Admin only

**Request Body:**
```json
{
  "serial_number": "CYL-2024-001",
  "cylinder_type": "13KG",
  "capacity_kg": 13.0,
  "manufacturer": "Greenwells Gas Company",
  "manufacturing_date": "2024-01-15",
  "expiry_date": "2039-01-15"
}
```

**Cylinder Types:**
- `6KG` - 6 kilogram cylinder
- `13KG` - 13 kilogram cylinder
- `26KG` - 26 kilogram cylinder
- `50KG` - 50 kilogram cylinder (commercial)

**Success Response (201 Created):**
```json
{
  "message": "Cylinder registered successfully",
  "cylinder": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "serial_number": "CYL-2024-001",
    "qr_code": "QR-A1B2C3D4E5F67890",
    "rfid_tag": "RFID-1234567890ABCDEF",
    "cylinder_type": "13KG",
    "capacity_kg": 13.0,
    "manufacturer": "Greenwells Gas Company",
    "manufacturing_date": "2024-01-15",
    "expiry_date": "2039-01-15",
    "status": "ACTIVE",
    "total_fills": 0,
    "total_scans": 0,
    "is_authentic": true,
    "is_tampered": false,
    "verification_status": "VERIFIED",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "security": {
    "qr_code": "QR-A1B2C3D4E5F67890",
    "rfid_tag": "RFID-1234567890ABCDEF",
    "auth_token": "abc123...xyz789:1705318200"
  }
}
```

**Validation Rules:**
- Serial number: Minimum 5 characters, alphanumeric with hyphens
- Capacity: Must match cylinder type
- Manufacturing date: Must be within last 20 years
- Expiry date: Must be in future, maximum 20 years from manufacturing

---

### 2. Scan and Verify Cylinder

**Endpoint:** `POST /cylinders/scan/`

**Description:** Scan QR code or RFID tag to verify cylinder authenticity and get complete information.

**Permissions:** All authenticated users (Customer, Driver, Dispatcher, Admin)

**Request Body:**
```json
{
  "code": "QR-A1B2C3D4E5F67890",
  "scan_type": "QR",
  "location_lat": -1.2921,
  "location_lng": 36.8219,
  "location_address": "123 Moi Avenue, Nairobi, Kenya",
  "order_id": 42
}
```

**Scan Types:**
- `QR` - QR code scan
- `RFID` - RFID tag scan
- `MANUAL` - Manual entry (tries both QR and RFID)

**Success Response (200 OK) - Valid Cylinder:**
```json
{
  "verified": true,
  "scan_result": "SUCCESS",
  "message": "Cylinder verified successfully",
  "cylinder": {
    "serial_number": "CYL-2024-001",
    "cylinder_type": "13KG",
    "capacity_kg": 13.0,
    "status": "FILLED",
    "manufacturer": "Greenwells Gas Company",
    "expiry_date": "2039-01-15",
    "total_fills": 12,
    "last_inspection_date": "2024-06-15"
  },
  "security": {
    "is_authentic": true,
    "is_tampered": false,
    "is_expired": false,
    "auth_token": "def456...uvw789:1705318200"
  },
  "customer": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "order": {
    "id": 42,
    "status": "IN_DELIVERY"
  }
}
```

**Response (200 OK) - Tampered Cylinder:**
```json
{
  "verified": false,
  "scan_result": "TAMPERED",
  "message": "Cylinder shows signs of tampering",
  "cylinder": {
    "serial_number": "CYL-2024-001",
    "cylinder_type": "13KG",
    "capacity_kg": 13.0,
    "status": "MAINTENANCE",
    "manufacturer": "Greenwells Gas Company",
    "expiry_date": "2039-01-15",
    "total_fills": 12,
    "last_inspection_date": "2024-06-15"
  },
  "security": {
    "is_authentic": false,
    "is_tampered": true,
    "is_expired": false,
    "auth_token": null
  }
}
```

**Response (200 OK) - Suspicious Activity Detected:**
```json
{
  "verified": true,
  "scan_result": "SUCCESS",
  "message": "Cylinder verified successfully",
  "cylinder": { ... },
  "security": { ... },
  "warning": {
    "is_suspicious": true,
    "reason": "Multiple rapid scans detected - possible cloning attempt",
    "action": "Report to security team immediately"
  }
}
```

**Scan Results:**
- `SUCCESS` - Valid, authentic cylinder
- `FAILED` - Invalid code or verification failed
- `SUSPICIOUS` - Suspicious activity detected
- `TAMPERED` - Cylinder has been tampered with
- `EXPIRED` - Cylinder has expired, needs inspection
- `STOLEN` - Cylinder reported as stolen

**Suspicious Activity Triggers:**
- More than 5 scans in 5 minutes
- Impossible location changes (>50km in 5 minutes)
- Scans from multiple distant locations simultaneously

---

### 3. Get Cylinder History

**Endpoint:** `GET /cylinders/{cylinder_id}/history/`

**Description:** Get complete history of all events for a specific cylinder.

**Permissions:**
- Customers: Can view history of their cylinders
- Drivers: Can view cylinders in their deliveries
- Dispatchers/Admins: Can view all cylinder history

**Query Parameters:**
- `event_type` (optional) - Filter by event type
- `start_date` (optional) - Filter from date (ISO 8601)
- `end_date` (optional) - Filter to date (ISO 8601)

**Success Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/cylinders/.../history/?page=2",
  "previous": null,
  "results": [
    {
      "id": 101,
      "cylinder": "550e8400-e29b-41d4-a716-446655440000",
      "cylinder_serial": "CYL-2024-001",
      "event_type": "DELIVERED",
      "event_date": "2024-01-20T14:30:00Z",
      "customer": 5,
      "customer_name": "John Doe",
      "driver": 3,
      "driver_name": "James Smith",
      "order": 42,
      "delivery": 18,
      "previous_status": "FILLED",
      "new_status": "IN_DELIVERY",
      "location": "123 Moi Avenue, Nairobi",
      "notes": "Assigned to order #42",
      "performed_by": 2,
      "performed_by_name": "dispatcher1",
      "verification_data": {
        "gps_coords": [-1.2921, 36.8219]
      }
    },
    {
      "id": 100,
      "cylinder": "550e8400-e29b-41d4-a716-446655440000",
      "cylinder_serial": "CYL-2024-001",
      "event_type": "FILLED",
      "event_date": "2024-01-20T10:00:00Z",
      "performed_by": 2,
      "performed_by_name": "dispatcher1",
      "previous_status": "EMPTY",
      "new_status": "FILLED",
      "location": "Main Warehouse",
      "notes": "Cylinder refilled and inspected"
    }
  ]
}
```

**Event Types:**
- `REGISTERED` - Initial cylinder registration
- `FILLED` - Cylinder filled with gas
- `DELIVERED` - Delivered to customer
- `RETURNED` - Returned from customer
- `SCANNED` - QR/RFID scan performed
- `INSPECTED` - Safety inspection completed
- `MAINTENANCE` - Maintenance work performed
- `STATUS_CHANGE` - Status manually changed
- `CUSTOMER_ASSIGNED` - Assigned to customer
- `CUSTOMER_UNASSIGNED` - Unassigned from customer
- `TAMPER_DETECTED` - Tampering detected
- `LOCATION_UPDATE` - Location manually updated

---

### 4. Assign Cylinder to Order/Customer

**Endpoint:** `POST /cylinders/assign/`

**Description:** Assign a cylinder to an order or customer for delivery tracking.

**Permissions:** Dispatcher, Admin only

**Request Body:**
```json
{
  "cylinder_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_id": 42,
  "notes": "Assigning 13KG cylinder for delivery"
}
```

OR

```json
{
  "cylinder_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": 5,
  "notes": "Long-term cylinder assignment"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Cylinder assigned successfully",
  "cylinder": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "serial_number": "CYL-2024-001",
    "status": "IN_DELIVERY",
    "current_customer": 5,
    "customer_name": "John Doe",
    "current_order": 42,
    "order_id": 42,
    ...
  }
}
```

---

### 5. Update Cylinder Status

**Endpoint:** `PATCH /cylinders/{cylinder_id}/status/`

**Description:** Update cylinder status with automatic history logging.

**Permissions:** Dispatcher, Admin only

**Request Body:**
```json
{
  "status": "MAINTENANCE",
  "notes": "Valve replacement required",
  "location": "Maintenance Workshop B"
}
```

**Cylinder Statuses:**
- `ACTIVE` - Active, ready for use
- `FILLED` - Filled with gas, ready for delivery
- `IN_DELIVERY` - Currently being delivered
- `EMPTY` - Empty, needs refilling
- `MAINTENANCE` - Under maintenance
- `RETIRED` - Permanently retired
- `STOLEN` - Reported stolen/lost

**Valid Status Transitions:**
```
ACTIVE → FILLED, MAINTENANCE, RETIRED, STOLEN
FILLED → IN_DELIVERY, EMPTY, MAINTENANCE
IN_DELIVERY → FILLED, EMPTY
EMPTY → FILLED, MAINTENANCE, RETIRED
MAINTENANCE → ACTIVE, RETIRED
RETIRED → (none - final state)
STOLEN → ACTIVE (if recovered)
```

**Success Response (200 OK):**
```json
{
  "message": "Cylinder status updated successfully",
  "cylinder": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "serial_number": "CYL-2024-001",
    "status": "MAINTENANCE",
    "last_known_location": "Maintenance Workshop B",
    ...
  }
}
```

---

### 6. Get Cylinder Details

**Endpoint:** `GET /cylinders/{cylinder_id}/`

**Description:** Get complete details for a specific cylinder including recent history and scans.

**Permissions:**
- Customers: Can view their cylinders
- Drivers: Can view cylinders in their deliveries
- Dispatchers/Admins: Can view all cylinders

**Success Response (200 OK):**
```json
{
  "cylinder": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "serial_number": "CYL-2024-001",
    "qr_code": "QR-A1B2C3D4E5F67890",
    "rfid_tag": "RFID-1234567890ABCDEF",
    "cylinder_type": "13KG",
    "capacity_kg": 13.0,
    "manufacturer": "Greenwells Gas Company",
    "manufacturing_date": "2024-01-15",
    "expiry_date": "2039-01-15",
    "status": "FILLED",
    "current_customer": 5,
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "last_known_location": "123 Moi Avenue, Nairobi",
    "last_scanned_at": "2024-01-20T14:30:00Z",
    "last_inspection_date": "2024-01-10",
    "next_inspection_date": "2025-01-10",
    "total_fills": 12,
    "total_scans": 45,
    "is_authentic": true,
    "is_tampered": false,
    "is_expired": false,
    "verification_status": "VERIFIED"
  },
  "recent_history": [
    { /* Last 10 history entries */ }
  ],
  "recent_scans": [
    { /* Last 5 scan logs */ }
  ]
}
```

---

### 7. List Cylinders

**Endpoint:** `GET /cylinders/`

**Description:** Get list of cylinders filtered by user role and query parameters.

**Permissions:**
- Customers: See only their cylinders
- Drivers: See cylinders in their deliveries
- Dispatchers/Admins: See all cylinders

**Query Parameters:**
- `status` - Filter by status
- `cylinder_type` - Filter by type (6KG, 13KG, 26KG, 50KG)
- `is_tampered` - Filter tampered cylinders (true/false)
- `is_expired` - Filter expired cylinders (true/false)

**Success Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/cylinders/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "serial_number": "CYL-2024-001",
      "cylinder_type": "13KG",
      "status": "FILLED",
      "customer_name": "John Doe",
      "is_tampered": false,
      "is_expired": false,
      "verification_status": "VERIFIED",
      ...
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid scan data",
  "details": {
    "code": ["Invalid code format."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied"
}
```

### 404 Not Found
```json
{
  "error": "Cylinder not found",
  "scan_result": "FAILED",
  "verified": false
}
```

## Security Best Practices

### For Frontend Integration

1. **Never store secret keys or auth hashes in frontend code**
2. **Always use HTTPS in production**
3. **Implement rate limiting on scan endpoints**
4. **Show clear warnings for tampered/suspicious cylinders**
5. **Log all scan attempts for security audit**

### For Mobile Apps

1. **Use secure storage for authentication tokens**
2. **Validate QR/RFID codes before sending to API**
3. **Request location permissions for GPS tracking**
4. **Implement offline queueing for scans in poor connectivity**
5. **Show visual indicators for verification status**

### For Backend Integration

1. **Regularly rotate JWT secret keys**
2. **Monitor for suspicious scan patterns**
3. **Set up alerts for tampered cylinder scans**
4. **Implement IP-based rate limiting**
5. **Regular security audits of scan logs**

## Example Usage

### JavaScript/TypeScript

```typescript
import { cylinderAPI } from './lib/api';

// Register new cylinder
const registerCylinder = async () => {
  try {
    const response = await cylinderAPI.registerCylinder({
      serial_number: 'CYL-2024-001',
      cylinder_type: '13KG',
      capacity_kg: 13.0,
      manufacturer: 'Greenwells Gas Company',
      manufacturing_date: '2024-01-15',
      expiry_date: '2039-01-15'
    });
    
    console.log('QR Code:', response.security.qr_code);
    console.log('RFID Tag:', response.security.rfid_tag);
    
    // Display QR code to print/save
    displayQRCode(response.security.qr_code);
  } catch (error) {
    console.error('Registration failed:', error);
  }
};

// Scan cylinder
const scanCylinder = async (qrCode: string) => {
  try {
    const position = await getCurrentPosition();
    
    const response = await cylinderAPI.scanCylinder({
      code: qrCode,
      scan_type: 'QR',
      location_lat: position.coords.latitude,
      location_lng: position.coords.longitude,
      location_address: await getAddressFromCoords(position.coords)
    });
    
    if (response.verified) {
      showSuccess('Cylinder verified successfully!');
      
      if (response.warning?.is_suspicious) {
        showWarning(response.warning.reason);
        alertSecurityTeam(response.warning);
      }
    } else {
      showError(`Verification failed: ${response.message}`);
      
      if (response.scan_result === 'TAMPERED') {
        showCriticalAlert('Tampered cylinder detected!');
      }
    }
  } catch (error) {
    console.error('Scan failed:', error);
  }
};

// Get cylinder history
const getCylinderHistory = async (cylinderId: string) => {
  try {
    const response = await cylinderAPI.getCylinderHistory(cylinderId);
    
    console.log('Total events:', response.total_events);
    
    response.history.forEach(event => {
      console.log(`${event.event_type} at ${event.event_date}`);
      console.log(`  Location: ${event.location}`);
      console.log(`  Notes: ${event.notes}`);
    });
  } catch (error) {
    console.error('Failed to get history:', error);
  }
};
```

### Python

```python
import requests

API_BASE_URL = 'http://localhost:8000/api'
ACCESS_TOKEN = 'your_jwt_token_here'

def scan_cylinder(qr_code, lat, lng):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'code': qr_code,
        'scan_type': 'QR',
        'location_lat': lat,
        'location_lng': lng
    }
    
    response = requests.post(
        f'{API_BASE_URL}/cylinders/scan/',
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if result['verified']:
            print('✓ Cylinder verified successfully')
            print(f"  Serial: {result['cylinder']['serial_number']}")
            print(f"  Status: {result['cylinder']['status']}")
            
            if 'warning' in result:
                print(f"⚠️  WARNING: {result['warning']['reason']}")
        else:
            print(f'✗ Verification failed: {result["message"]}')
    else:
        print(f'Error: {response.status_code}')

# Usage
scan_cylinder('QR-A1B2C3D4E5F67890', -1.2921, 36.8219)
```

## Testing

Run comprehensive tests:

```bash
cd backend
python manage.py test orders.tests.CylinderAPITestCase
```

## Support

For API support or to report security issues:
- Email: security@greenwells.com
- Security Hotline: +254-XXX-XXXXXX
- Emergency: Report tampered cylinders immediately

## Version History

- **v1.0.0** (2024-01-15) - Initial release
  - Cylinder registration with QR/RFID generation
  - Scan verification with security checks
  - Complete history tracking
  - Suspicious activity detection
  - GPS location tracking
