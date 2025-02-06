We are looking to build an e-commerce application with following features -
    1. Users can sign up, login and purchase available products of various brands. Username is unique for each user.
    2. There are platform admins (one or more) an admin can only create another admin, but cannot remove either the admin nor the user
    3. admins can login to their domain to add/update/remove products. Further, they can also manage the available quantity of products.
    4. Admins, neither user cannot login to another domain
    5. Products can be categorized and filtered based on category.
    6. Products can be searched by their name. List all products that contains the search field in their name.
    7. Users can create order items. An order item consists of product and quantity.
    8. An order item for a product can be created only when the quantity is less than its available quantity.
    9. An order consists of order items, total quantity and total amount.
    10. Users can view their order history.
Build an application with FastAPI and implement login with Keycloak. You are expected to - 
    1. Define Models for User,Admins, Role, Product, Order and OrderItems with correct mapping.
    2. Implement multi-admin for Products. Endpoints should be at admin level (/adminName/endpoint).
    3. Add necessary endpoints and routing to carry out each task.
    4. Adhere to the permissions and privileges to each role – Admin and User roles.
    5. Implement pagination wherever necessary.
    6. Implement error handling wherever required.
  
Bonus - Implement favourite product for users. User should be able to mark/unmark a product as favourite and retrieve the list of favourite products.