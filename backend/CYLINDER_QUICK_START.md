# LPG Cylinder QR/RFID Tracking - Quick Start Guide

## 🚀 Overview

This system provides complete tracking and authenticity verification for LPG cylinders using QR codes and RFID tags. Built with enterprise-level security standards.

## 🔑 Key Features

- ✅ **QR/RFID Code Generation** - Automatic unique code generation
- ✅ **Authenticity Verification** - Cryptographic validation
- ✅ **Tamper Detection** - Automated suspicious activity detection
- ✅ **Complete History** - Track every cylinder event
- ✅ **GPS Tracking** - Real-time location monitoring
- ✅ **Security Audit** - Complete logging for compliance

## 📋 Prerequisites

```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Database migrations
python manage.py migrate
```

## 🎯 Quick Start

### 1. Register a Cylinder (Dispatcher/Admin)

```bash
curl -X POST http://localhost:8000/api/cylinders/register/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "CYL-2024-001",
    "cylinder_type": "13KG",
    "capacity_kg": 13.0,
    "manufacturer": "Greenwells Gas Co.",
    "manufacturing_date": "2024-01-01",
    "expiry_date": "2039-01-01"
  }'
```

**Response includes:**
- QR Code for printing
- RFID Tag for programming
- Auth token for verification

### 2. Scan a Cylinder (Any User)

```bash
curl -X POST http://localhost:8000/api/cylinders/scan/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "QR-A1B2C3D4E5F67890",
    "scan_type": "QR",
    "location_lat": -1.2921,
    "location_lng": 36.8219,
    "location_address": "123 Main St, Nairobi"
  }'
```

**Verification Results:**
- ✅ SUCCESS - Valid cylinder
- ❌ TAMPERED - Security breach detected
- ⚠️ EXPIRED - Needs inspection
- 🚫 STOLEN - Reported lost/stolen

### 3. Get Cylinder History

```bash
curl -X GET http://localhost:8000/api/cylinders/{CYLINDER_ID}/history/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Shows complete lifecycle:**
- Registration
- Fills and refills
- Customer assignments
- Deliveries
- Scans and verifications
- Maintenance records
- All status changes

## 🔐 Security Features

### Tamper Detection

The system automatically detects:
- Multiple rapid scans (>5 in 5 minutes)
- Impossible location changes
- Manual tamper flags

### Cryptographic Verification

- SHA-256 authentication hash
- Secret key for token generation
- Time-limited auth tokens
- IP address logging

### Audit Trail

Every action is logged:
- Who scanned
- When scanned
- Where scanned
- What was the result

## 📱 Frontend Integration

### TypeScript/React

```typescript
import { cylinderAPI } from './lib/api';

// Scan cylinder
const scanResult = await cylinderAPI.scanCylinder({
  code: qrCode,
  scan_type: 'QR',
  location_lat: latitude,
  location_lng: longitude,
  location_address: address
});

if (scanResult.verified) {
  console.log('✓ Valid cylinder');
} else {
  console.error('✗ Invalid:', scanResult.message);
}
```

### Mobile App

```javascript
// React Native example
import QRCodeScanner from 'react-native-qrcode-scanner';
import * as Location from 'expo-location';

const CylinderScanner = () => {
  const onScan = async (e) => {
    // Get current location
    const location = await Location.getCurrentPositionAsync();
    
    // Verify cylinder
    const result = await cylinderAPI.scanCylinder({
      code: e.data,
      scan_type: 'QR',
      location_lat: location.coords.latitude,
      location_lng: location.coords.longitude
    });
    
    if (result.verified) {
      Alert.alert('Success', 'Cylinder verified!');
    } else if (result.scan_result === 'TAMPERED') {
      Alert.alert('Warning', 'Tampered cylinder detected!');
    }
  };
  
  return <QRCodeScanner onRead={onScan} />;
};
```

## 🧪 Testing

Run all tests:
```bash
cd backend
python manage.py test orders.tests.CylinderAPITestCase
```

Expected output:
```
test_register_cylinder_success ... ok
test_scan_cylinder_qr_success ... ok
test_scan_cylinder_tampered ... ok
test_get_cylinder_history ... ok
...

Ran 6 tests in 5.5s - OK
```

## 📊 Use Cases

### 1. Customer Delivery
```
1. Driver scans cylinder QR code
2. System verifies authenticity
3. Customer location recorded
4. Delivery history updated
5. Customer can track cylinder lifecycle
```

### 2. Refill Station
```
1. Operator scans cylinder
2. System checks expiry and safety
3. Records fill event
4. Updates cylinder status to FILLED
5. Ready for next delivery
```

### 3. Security Audit
```
1. Security team views scan logs
2. Identifies suspicious patterns
3. Flags tampered cylinders
4. Generates compliance reports
```

### 4. Maintenance Inspection
```
1. Technician scans cylinder
2. Records inspection results
3. Updates next inspection date
4. Flags cylinders for maintenance
```

## 🎨 Cylinder Status Flow

```
ACTIVE → FILLED → IN_DELIVERY → EMPTY → FILLED (cycle repeats)
                    ↓
                MAINTENANCE → ACTIVE
                    ↓
                RETIRED (end of life)
```

## ⚠️ Important Notes

### Security
- Never expose secret keys or auth hashes
- Always use HTTPS in production
- Implement rate limiting on scan endpoints
- Monitor suspicious activity logs daily

### Compliance
- Cylinder expiry dates must be monitored
- Inspections required before expiry
- Tampered cylinders must be quarantined
- Complete audit trail maintained

### Performance
- Scan responses < 200ms typical
- History queries paginated (20 items/page)
- GPS coordinates optional but recommended
- Offline queue supported for poor connectivity

## 📖 Full Documentation

See `CYLINDER_API_DOCUMENTATION.md` for:
- Complete API reference
- All endpoint details
- Error handling
- Security best practices
- Advanced examples

## 🆘 Troubleshooting

### "Cylinder not found"
- Verify QR/RFID code is correct
- Check code hasn't been tampered with
- Ensure cylinder is registered in system

### "Permission denied"
- Check user role permissions
- Verify JWT token is valid
- Ensure user is assigned to cylinder/order

### "Suspicious activity detected"
- Review scan pattern in logs
- Check if multiple devices scanning same code
- Verify GPS coordinates are reasonable
- Contact security team if confirmed issue

## 📞 Support

- **Documentation**: See full API docs
- **Security Issues**: Report immediately to security team
- **Bug Reports**: Create GitHub issue
- **Feature Requests**: Submit enhancement request

## 🔄 Updates

Check the migration files for schema updates:
```bash
python manage.py showmigrations orders
```

Latest migration: `0004_cylinder_cylinderhistory_cylinderscan_and_more`

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Status**: Production Ready ✅
