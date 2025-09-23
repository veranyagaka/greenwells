# Orders API Documentation

This documentation covers the Orders management system for the LPG delivery platform, providing comprehensive order creation, driver assignment, and real-time tracking functionality.

## Overview

The Orders API provides a complete order management system with the following capabilities:
- **Order Creation**: Customers can create delivery orders with detailed specifications
- **Smart Driver Assignment**: Automated assignment of nearest available drivers
- **Real-time Status Tracking**: Complete order lifecycle management
- **Location Tracking**: GPS-based delivery tracking
- **Role-based Security**: Different access levels for customers, drivers, dispatchers, and admins

## Database Schema

The Orders app implements the following models based on the Ugunja.pdf schema:

### Core Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| **Vehicle** | Delivery vehicles | plate_number, model, capacity_kg, status |
| **DriverAssignment** | Driver-to-vehicle assignments | driver, vehicle, start_date, end_date |
| **Order** | Customer delivery requests | customer, delivery_address, quantity_kg, status |
| **Delivery** | Order fulfillment tracking | order, driver, vehicle, assigned_by |
| **TrackingLog** | Real-time location tracking | delivery, latitude, longitude, timestamp |

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

All endpoints require JWT authentication via the `Authorization: Bearer <token>` header.

---

## 1. Order Management

### Create Order

**Endpoint:** `POST /api/orders/create/`

**Description:** Create a new LPG delivery order. Only customers can create orders.

**Permissions:** Customer role required

**Request Body:**
```json
{
  "delivery_address": "123 Main Street, Nairobi, Kenya",
  "quantity_kg": 25.0,
  "scheduled_time": "2024-01-15T14:30:00Z",
  "pickup_address": "LPG Depot, Industrial Area",
  "customer_phone": "+254712345678",
  "special_instructions": "Call before arrival, gate code 1234"
}
```

**Field Validations:**
- `delivery_address`: Required, text field
- `quantity_kg`: Required, must be > 0 and ≤ 1000
- `scheduled_time`: Required, must be in the future, max 30 days ahead
- `pickup_address`: Optional, defaults to main depot
- `customer_phone`: Optional, phone number
- `special_instructions`: Optional, additional delivery notes

**Success Response (201 Created):**
```json
{
  "message": "Order created successfully",
  "order": {
    "id": 1,
    "customer": 1,
    "customer_name": "john_doe",
    "customer_email": "john@example.com",
    "delivery_address": "123 Main Street, Nairobi, Kenya",
    "pickup_address": "LPG Depot, Industrial Area",
    "quantity_kg": 25.0,
    "status": "PENDING",
    "scheduled_time": "2024-01-15T14:30:00Z",
    "customer_phone": "+254712345678",
    "special_instructions": "Call before arrival, gate code 1234",
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-10T10:00:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Validation errors
- `403 Forbidden`: Non-customer attempting to create order
- `500 Internal Server Error`: Server error

---

### List Orders

**Endpoint:** `GET /api/orders/`

**Description:** Retrieve orders based on user role with pagination support.

**Permissions:** Authenticated users

**Access Control:**
- **Customers**: See only their own orders
- **Drivers**: See orders assigned to them
- **Dispatchers/Admins**: See all orders

**Query Parameters:**
- `status`: Filter by order status (PENDING, ASSIGNED, ON_ROUTE, DELIVERED, CANCELLED)
- `page`: Page number for pagination
- `page_size`: Number of results per page (max 100)

**Example Request:**
```
GET /api/orders/?status=PENDING&page=1&page_size=20
```

**Success Response (200 OK):**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "customer": 1,
      "customer_name": "john_doe",
      "customer_email": "john@example.com",
      "delivery_address": "123 Main Street, Nairobi",
      "quantity_kg": 25.0,
      "status": "PENDING",
      "scheduled_time": "2024-01-15T14:30:00Z",
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

---

### Get Order Details

**Endpoint:** `GET /api/orders/{order_id}/`

**Description:** Retrieve detailed information about a specific order.

**Permissions:** 
- **Customers**: Own orders only
- **Drivers**: Assigned orders only
- **Dispatchers/Admins**: All orders

**Success Response (200 OK):**
```json
{
  "order": {
    "id": 1,
    "customer": 1,
    "customer_name": "john_doe",
    "customer_email": "john@example.com",
    "delivery_address": "123 Main Street, Nairobi",
    "quantity_kg": 25.0,
    "status": "ASSIGNED",
    "scheduled_time": "2024-01-15T14:30:00Z",
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-10T12:00:00Z",
    "delivery": {
      "id": 1,
      "driver": 2,
      "driver_name": "driver_mike",
      "vehicle": 1,
      "vehicle_plate": "KCA-123A",
      "assigned_by": 3,
      "assigned_by_name": "dispatcher_jane",
      "assigned_at": "2024-01-10T12:00:00Z",
      "status": "ASSIGNED"
    }
  }
}
```

**Error Responses:**
- `403 Forbidden`: Permission denied
- `404 Not Found`: Order not found

---

## 2. Driver Assignment

### Assign Driver to Order

**Endpoint:** `POST /api/orders/assign-driver/`

**Description:** Assign a driver and vehicle to a pending order. Can specify driver/vehicle or let system find nearest available.

**Permissions:** Dispatcher or Admin role required

**Request Body (Specific Assignment):**
```json
{
  "order_id": 1,
  "driver_id": 2,
  "vehicle_id": 1
}
```

**Request Body (Auto Assignment):**
```json
{
  "order_id": 1
}
```

**Field Descriptions:**
- `order_id`: Required, must be a PENDING order
- `driver_id`: Optional, specific driver to assign
- `vehicle_id`: Optional, specific vehicle to assign

**Success Response (201 Created):**
```json
{
  "message": "Driver assigned successfully",
  "delivery": {
    "id": 1,
    "order_id": 1,
    "driver": 2,
    "driver_name": "driver_mike",
    "vehicle": 1,
    "vehicle_plate": "KCA-123A",
    "assigned_by": 3,
    "assigned_by_name": "dispatcher_jane",
    "assigned_at": "2024-01-10T12:00:00Z",
    "status": "ASSIGNED"
  }
}
```

**Assignment Logic:**
1. If driver_id not provided, system finds nearest available driver
2. If vehicle_id not provided, uses driver's currently assigned vehicle
3. Creates Delivery record linking order, driver, and vehicle
4. Updates order status to "ASSIGNED"

**Error Responses:**
- `400 Bad Request`: Order already assigned, no available drivers, validation errors
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Order, driver, or vehicle not found

---

## 3. Status Management

### Update Order Status

**Endpoint:** `PATCH /api/orders/{order_id}/status/`

**Description:** Update order status with proper state transition validation.

**Permissions:**
- **Drivers**: Can update orders assigned to them
- **Dispatchers/Admins**: Can update any order

**Request Body:**
```json
{
  "status": "ON_ROUTE"
}
```

**Valid Status Transitions:**
```
PENDING → ASSIGNED, CANCELLED
ASSIGNED → ON_ROUTE, CANCELLED  
ON_ROUTE → DELIVERED, CANCELLED
DELIVERED → (final state)
CANCELLED → (final state)
```

**Success Response (200 OK):**
```json
{
  "message": "Order status updated successfully",
  "order": {
    "id": 1,
    "status": "ON_ROUTE",
    "updated_at": "2024-01-10T14:00:00Z"
  }
}
```

**Automatic Side Effects:**
- `ON_ROUTE`: Updates delivery status to "IN_PROGRESS", sets started_at timestamp
- `DELIVERED`: Updates delivery status to "COMPLETED", sets completed_at timestamp
- `CANCELLED`: Updates delivery status to "FAILED" with failure reason

**Error Responses:**
- `400 Bad Request`: Invalid status transition
- `403 Forbidden`: Permission denied
- `404 Not Found`: Order not found

---

## 4. Real-time Tracking

### Add Tracking Log

**Endpoint:** `POST /api/tracking/`

**Description:** Add GPS location data for active delivery tracking.

**Permissions:** Driver, Dispatcher, or Admin

**Request Body:**
```json
{
  "delivery": 1,
  "latitude": -1.2921,
  "longitude": 36.8219,
  "speed": 45.5,
  "heading": 275.0,
  "accuracy": 5.0
}
```

**Field Validations:**
- `delivery`: Required, must be valid delivery ID
- `latitude`: Required, range -90 to 90
- `longitude`: Required, range -180 to 180
- `speed`: Optional, km/h
- `heading`: Optional, degrees (0-360)
- `accuracy`: Optional, GPS accuracy in meters

**Success Response (201 Created):**
```json
{
  "message": "Tracking log added successfully",
  "tracking_log": {
    "id": 1,
    "delivery": 1,
    "latitude": -1.2921,
    "longitude": 36.8219,
    "speed": 45.5,
    "heading": 275.0,
    "accuracy": 5.0,
    "timestamp": "2024-01-10T14:30:00Z"
  }
}
```

---

### Get Delivery Tracking

**Endpoint:** `GET /api/tracking/{delivery_id}/`

**Description:** Retrieve all tracking logs for a specific delivery.

**Permissions:**
- **Customers**: Can track their own orders
- **Drivers**: Can see tracking for their deliveries
- **Dispatchers/Admins**: Can see all tracking data

**Success Response (200 OK):**
```json
{
  "delivery_id": 1,
  "tracking_logs": [
    {
      "id": 5,
      "latitude": -1.2921,
      "longitude": 36.8219,
      "speed": 45.5,
      "heading": 275.0,
      "timestamp": "2024-01-10T14:30:00Z"
    },
    {
      "id": 4,
      "latitude": -1.2855,
      "longitude": 36.8175,
      "speed": 38.2,
      "heading": 280.0,
      "timestamp": "2024-01-10T14:25:00Z"
    }
  ]
}
```

---

## Security Features

### Authentication & Authorization
- **JWT Token Required**: All endpoints require valid JWT authentication
- **Role-based Access Control**: Different permissions for each user role
- **Input Validation**: Comprehensive validation on all inputs
- **SQL Injection Prevention**: Using Django ORM for all database operations

### Data Security
- **Permission Boundaries**: Users can only access their relevant data
- **Audit Trail**: All actions logged with user attribution
- **Status Validation**: Prevents invalid state transitions
- **Rate Limiting**: Built-in pagination to prevent abuse

### Error Handling
- **Secure Error Messages**: No sensitive information exposed
- **Consistent Response Format**: Standardized error responses
- **Logging**: Comprehensive logging for debugging and monitoring

---

## User Roles & Permissions

| Role | Create Order | View Orders | Assign Driver | Update Status | Add Tracking | View Tracking |
|------|--------------|-------------|---------------|---------------|--------------|---------------|
| **CUSTOMER** | ✅ Own | ✅ Own | ❌ | ❌ | ❌ | ✅ Own |
| **DRIVER** | ❌ | ✅ Assigned | ❌ | ✅ Assigned | ✅ Own | ✅ Own |
| **DISPATCHER** | ❌ | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All |
| **ADMIN** | ❌ | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All |

---

## Usage Examples

### Customer Creating an Order

```bash
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_address": "123 Main Street, Nairobi",
    "quantity_kg": 25.0,
    "scheduled_time": "2024-01-15T14:30:00Z",
    "customer_phone": "+254712345678"
  }'
```

### Dispatcher Assigning Driver

```bash
curl -X POST http://localhost:8000/api/orders/assign-driver/ \
  -H "Authorization: Bearer <dispatcher_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "driver_id": 2
  }'
```

### Driver Updating Status

```bash
curl -X PATCH http://localhost:8000/api/orders/1/status/ \
  -H "Authorization: Bearer <driver_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ON_ROUTE"
  }'
```

### Adding GPS Tracking

```bash
curl -X POST http://localhost:8000/api/tracking/ \
  -H "Authorization: Bearer <driver_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery": 1,
    "latitude": -1.2921,
    "longitude": 36.8219,
    "speed": 45.5
  }'
```

---

## Error Codes & Messages

| HTTP Code | Description | Common Causes |
|-----------|-------------|---------------|
| **400** | Bad Request | Invalid input data, validation errors |
| **401** | Unauthorized | Missing or invalid JWT token |
| **403** | Forbidden | Insufficient permissions for action |
| **404** | Not Found | Order, driver, or vehicle doesn't exist |
| **500** | Internal Server Error | Unexpected server error |

### Common Error Response Format

```json
{
  "error": "Brief error description",
  "details": {
    "field_name": ["Specific validation error message"]
  }
}
```

---

## Testing

The Orders API includes comprehensive test coverage:

### Running Tests
```bash
cd backend
python manage.py test orders
```

### Test Coverage
- **Model Tests**: Validation, relationships, constraints
- **API Tests**: All endpoints with various scenarios
- **Permission Tests**: Role-based access control
- **Validation Tests**: Input validation and error handling
- **Integration Tests**: End-to-end order lifecycle

---

## Production Considerations

### Performance Optimization
- **Database Indexing**: Optimized queries with proper indexes
- **Pagination**: Prevents large result sets
- **Select Related**: Minimizes database queries
- **Caching**: Consider implementing Redis for frequently accessed data

### Monitoring & Logging
- **Audit Logs**: All order actions logged with user attribution
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Track API response times
- **Business Metrics**: Order completion rates, delivery times

### Scalability
- **Horizontal Scaling**: Stateless design supports multiple instances
- **Database Optimization**: Proper indexing and query optimization
- **Background Tasks**: Consider Celery for heavy operations
- **API Rate Limiting**: Implement rate limiting for production

---

## Future Enhancements

### Planned Features
- **Advanced Driver Assignment**: Machine learning-based optimal assignment
- **Real-time Notifications**: WebSocket-based live updates
- **Route Optimization**: Integration with mapping services
- **Payment Integration**: Order payment processing
- **Analytics Dashboard**: Business intelligence and reporting
- **Mobile App Support**: Enhanced mobile-specific endpoints

### Integration Opportunities
- **SMS Notifications**: Order status updates via SMS
- **Email Notifications**: Automated email notifications
- **Mapping Services**: Google Maps/OpenStreetMap integration
- **Payment Gateways**: M-Pesa, Stripe, PayPal integration
- **Third-party Logistics**: Integration with external delivery services

---

## Support & Maintenance

For technical support or feature requests, please contact the development team or create an issue in the project repository.

**API Version:** 1.0  
**Last Updated:** January 2024  
**Documentation Version:** 1.0