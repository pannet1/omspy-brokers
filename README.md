## Broker add-ons for omspy


This repository provides connectors to various live brokers.

To implement a broker

1. Subclass from `omspy.base.Broker`
2. Implement the following 4 methods

### `authenticate`
authenticate the user
### `order_place`
to place a new order
### `order_modify`
to modify an existing order
### `order_cancel`
to cancel an existing order

3. Create the following 3 methods as properties
### `orders`
should return a list of all orders
### `positions`
should return a list of all existing positions
### `trades`
should return a list of all trades

Implement any other broker method you wish to implement
and also override any existing method
