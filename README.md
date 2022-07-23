# django-product-server

REST API product server allowing to add and get information about products and categories 

## install:
```
git clone 

cd django-product-server 

docker build --tag product-server .

docker run --publish 8000:8000 product-server

```
## API: 
### `/api/all` [GET] 
Show all products and categroies
### `/api/imports` [POST] 
Add some items. If such id already exists, item updates \
example of request body: 
```
{
  "items": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66a111",
      "name": "Category 1",
      "parentId": "null",
      "price": 234,
      "type": "CATEGORY"
    },
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66a222",
      "name": "Offer 1",
      "parentId": "3fa85f64-5717-4562-b3fc-2c963f66a111",
      "price": 234,
      "type": "OFFER"
    }
  ],
  "updateDate": "2022-05-20T23:12:01.000Z"
}
```
### `/api/nodes/<id>` [GET]
Get info about item with given id
### `/api/node/<id>/statistic` [GET]
Get statistics about all changes in item with given id
### `/api/sales?date=<date>` [GET]
Get all items which are changed during last 24 hours from given date
### `/api/delete/<id>` [DELETE]
Removes item with given id and all statistics related to it
