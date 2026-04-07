# Payment Service API (Equipo 4)

## Base URL local

`http://localhost:8004/api`

## Endpoint principal

### POST /payments/process/

Procesa el pago de un pedido existente y, si es exitoso, solicita al Order Service cambiar el estado a `Pagado`.

#### Request JSON

```json
{
  "order_id": 100,
  "user_id": 50,
  "card_number": "4111111111111111",
  "expiration_date": "12/30",
  "cvv": "123"
}
```

#### Validaciones

- `order_id`: entero positivo.
- `user_id`: entero positivo.
- `card_number`: exactamente 16 dígitos.
- `expiration_date`: formato `MM/YY`.
- `cvv`: exactamente 3 dígitos.

#### Respuestas

- `201 Created`: pago creado y pedido actualizado a `Pagado`.
- `202 Accepted`: pago creado pero no se pudo actualizar el estado del pedido.
- `400 Bad Request`: datos inválidos o usuario no coincide con el pedido.
- `404 Not Found`: pedido no encontrado en Order Service.
- `409 Conflict`: pedido ya pagado o enviado.
- `502 Bad Gateway`: respuesta inválida del Order Service (sin total).

#### Response JSON (201)

```json
{
  "id": 1,
  "order_id": 100,
  "user_id": 50,
  "total": "999.99",
  "card_number": "**** **** **** 1111",
  "expiration_date": "12/30",
  "cvv": null,
  "status": "Completed",
  "created_at": "2026-04-06T12:00:00Z"
}
```

## Integraciones externas

- GET `http://localhost:8003/api/orders/{order_id}/`
- PATCH `http://localhost:8003/api/orders/{order_id}/status/` con body JSON:

```json
{
  "status": "Pagado"
}
```
