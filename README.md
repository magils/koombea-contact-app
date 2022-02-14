# Koombea Contacts App

### Deployment 

To run this app you will need Docker and docker-compose on your system. If they are already installed, go to the root of the project folder and execute:

`docker-compose up`


## Endpoints

All endpoints are protected by JWT, in order to access them you will need to register an user and then login, to do that use the following endpoints:

- `[POST] /signup`: Register a new user. You must provide a valid email and password.
```
 {
    "email": "testy1@test.com",
    "password": "Pass123"
}
```

- `[POST] localhost:5000/login`: Using valid email and password, generates a JWT token, which the user can use to get access to the endpoints:

```
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0NDgwMzQ0OSwianRpIjoiY2U0MWU1MTAtYTBkYy00YjQ5LTkxMjMtNGNlODNkOTc2ODUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjQ0ODAzNDQ5LCJleHAiOjE2NDQ4ODk4NDl9.7Xvt0X45yhftMSsVpKeNtepDx_B6idanpnc7yCtiWL9Q"
}
```

- `[POST] /contacts` : Allows to upload contacts using a CSV file. This endpoint uses `form-data` request, and has 2 
key values: `file (required)` for the CSV file path and `field-mapping` for custom column names, for example:

```
{
	"name": "nm",
	"birthdate": "b_date",
	"phone": "phn",
	"address": "addr",
	"credit_card": "cc"
}
```

For the `name` value, the API will look for the column `nm` in the file and so on. This gives the freedom to upload files without modifying the header columns.

- `[GET] /uploads`: Returns uploads history.

```
{
    "uploads": [
        {
            "file_name": "contacts-valid.csv",
            "id": 2,
            "lines_failed": 0,
            "lines_imported": 4,
            "status": "TERMINATED",
            "upload_date": "Mon, 14 Feb 2022 01:33:38 GMT",
            "user": 1
        }
    ]
}
```

- `[GET] contacts/uploads/<import_id>`: Returns the list of contacts of an upload. To use the endpoint, after uploading a file, copy the value of `import_id` in the response and paste it in the `<import_id>`. This endpoint supports pagination, to paginate use the query param `page`.

```
{
    "contacts": [
        {
            "address": "Some place in Earth",
            "birthdate": "2000 January 11",
            "credit_card": "**********4631",
            "email": "mario@test.com",
            "franchise": "Visa",
            "name": "Mario",
            "phone": "(+57) 320-432-05-12"
        },
        {
            "address": "Some place in Earth",
            "birthdate": "2011 January 23",
            "credit_card": "**********8311",
            "email": "peter@test.com",
            "franchise": "Mastercard",
            "name": "Peter",
            "phone": "(+57) 320-432-05-14"
        }
    ]
}
```

- `[POST] /logout`: Revokes the current token.


### Testing with Postman

To get started a Postman collection is included in the project. To use it, first import it and then go to the requests: `User Sign In`, if you do not have an user, and then `User login` to generate a JWT Token. After generating the token, click on `Koombea Contacts`, click in the text field `Token`, copy the token generated and finally save it. After that you should be ready to use any method of the API.



### Sample files

It is included as well several files to test multiple scenarios. This files are located in the `resources` folder of the project. These files are:

- `contacts-valid.csv`: A valid CSV file which will import all contacts without any errors.

- `contacts-duplicated.csv`: CSV file which should fail because contains duplicated email addresses.

- `contacts-invalid-data.csv`: CSV file with invalid fields, after import some fields should be `null`.

- `contacts-custom_fields.csv`: File with custom header names. To test it, use this payload to match the fields with the desire values:

```
{
  "name": "nm",
  "birthdate": "bd",
  "phone": "phn",
  "address": "addr",
  "credit_card": "cc",
  "email": "mail"
}

```