# TaskFlow API Specification v2.1

**Base URL**: `https://api.taskflow.io/v2`
**Authentication**: Required for all endpoints

---

## Authentication

All requests must include a valid API key. Include the key in the request header.

## Endpoints

### GET /tasks

Retrieve a list of tasks for the authenticated user.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status: `active`, `completed`, `archived` |
| `page` | integer | No | Page number for pagination |
| `per_page` | integer | No | Results per page |

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "status": "string",
      "assignee": "string",
      "due_date": "string",
      "priority": "string"
    }
  ],
  "total": "integer"
}
```

### POST /tasks

Create a new task.

**Request Body**:
```json
{
  "title": "string (required)",
  "description": "string",
  "assignee": "string",
  "due_date": "string",
  "priority": "string"
}
```

**Response** (201 Created):
```json
{
  "id": "string",
  "title": "string",
  "status": "active",
  "created_at": "string"
}
```

### PUT /tasks/{id}

Update an existing task.

**Request Body**:
```json
{
  "title": "string",
  "description": "string",
  "assignee": "string",
  "due_date": "string",
  "priority": "integer",
  "status": "string"
}
```

**Response** (200 OK):
```json
{
  "id": "string",
  "title": "string",
  "status": "string",
  "assignee": "string",
  "due_date": "string",
  "priority": "string",
  "updated_at": "string"
}
```

### DELETE /tasks/{id}

Delete a task. The task is permanently removed.

**Response** (204 No Content): Empty response body.

## Rate Limiting

API requests are rate limited. Exceeding the rate limit returns HTTP 429.

## Error Handling

Errors are returned in a standard format:
```json
{
  "error": "string",
  "message": "string"
}
```

## Webhooks

TaskFlow supports webhooks for task events. Configure webhooks in your account settings. Events include task creation, completion, and assignment changes.

## Data Retention

Deleted tasks are permanently removed. Completed tasks are retained for a reasonable period.
