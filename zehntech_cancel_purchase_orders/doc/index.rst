================================================================
Cancel Purchase Orders
================================================================

Provides flexible options for canceling purchase orders, including resetting to draft, deleting purchase, and bulk cancellation capabilities.

**Table of Contents**

.. contents::
   :local:

**Key Features**
================================================================

- **Smart & Bulk Order Cancellation**:  
  The **Smart & Bulk Order Cancellation** feature provides multiple cancellation options, including **Cancel Only, Cancel and Reset to Draft, and Cancel and Delete**, allowing users to manage orders efficiently.  
  **Bulk actions** enable quick processing of multiple purchase orders, saving time and ensuring consistency across operations.

- **Associated Record Handling**:  
  **Associated Record Handling** ensures that when a purchase order is canceled, related deliveries and bills can also be canceled automatically.  
  This prevents inconsistencies, **keeps records synchronized**, and allows businesses to manage order cancellations efficiently.

- **Data History Management**:  
  With **Data History Management**, a detailed log of canceled, reset, and deleted orders is maintained.  
  This ensures **transparency, accountability, and easy restoration** of previously canceled purchases orders, preventing accidental data loss and allowing businesses to track all modifications.

- **Permanent Delete and Restore Records**:  
  The **Permanent Delete and Restore Records** functionality allows complete removal of purchase orders and related documents.  
  It also enables **data restoration**, such as bills and deliveries.  
  This helps maintain a **clean database** by eliminating unnecessary or duplicate records while ensuring that only authorized users can perform deletions.

- **Access Control for Users**:  
  The **Access Control for Users** feature lets administrators **assign specific permissions** for canceling purchases orders.  
  Businesses can restrict actions like permanent deletion and bulk cancellations, ensuring **role-based access** and preventing unauthorized modifications.

- **Intuitive Cancel purchases Dashboard**:  
  The **Intuitive Cancel purchases Dashboard** offers a **real-time overview** of canceled, draft, and confirmed purchase orders.  
  With **bar charts and a Kanban view**, users can track order statuses at a glance, access quick actions, and manage purchases operations more efficiently.

**Summary**
================================================================

The **purchase Order Cancel Management** module enhances the functionality of purchase orders by providing users with flexible cancellation options. Users can:

- Cancel purchase orders without affecting receipts or invoice statuses.
- Reset purchase orders and their associated receipts and invoice records to draft for further modifications.
- Permanently delete purchase orders along with all related records.
- Perform bulk cancellations directly from the purchase order list view.
- Cancel associated receipts and invoice records during the cancellation process.

**Installation**
================================================================

1. **Download** the module from the Odoo App Store or clone the repository.
2. **Place** the module in your Odoo addons directory.
3. **Update** your Odoo module list to recognize the new addition.
4. **Install** the module using Odoo's app interface.

**Usage Guide**
================================================================

**For Users**  
---------------------------------------------------------
Users can **access purchase order cancellation features** only if **granted permission by the administrator**.  
Depending on the permissions, users may have access to **Cancel Only, Reset to Draft, Cancel and Delete, or Bulk Cancellation**.

1. **Cancel a purchase Order** 

      **Path:** purchases > Orders > Open purchases Order  

- Open the purchase order that needs to be canceled.
- Depending on permissions, choose one of the following options:  
   **Cancel Only** – Marks the purchase order as "Cancelled" while keeping related deliveries and bills intact.  
   **Cancel and Reset to Draft** – Reverts the purchase order and its related records to **Draft**, allowing modifications.  
   **Cancel and Delete** – Permanently removes the purchase order and all linked records from the system.  

  If an option is missing, your **administrator has restricted access**.

2. **Cancel Associated Records**

      **Path:** purchases > Orders > Open purchases Order  

- If allowed, enable the **Cancel Associated Records** checkbox to cancel deliveries and bills **along with the purchase order**.  
   This keeps all related transactions synchronized.

3. **Perform Bulk Cancellations**  

      **Path:** purchases > Orders > List View  

- **Select multiple purchase orders** that need to be canceled.  
- Click on the **Action** menu and choose one of the available bulk actions:  
   **Bulk Cancel Only** – Cancels selected orders while keeping deliveries and bills unchanged.  
   **Bulk Reset to Draft** – Reverts selected orders and their associated records to **Draft**.  
   **Bulk Cancel and Delete** – Permanently removes selected orders and their related records.  

  If bulk cancellation options are not visible, your **administrator has restricted this functionality**.



**For Administrators**  
-----------------------------------------------
Administrators **automatically** have full access to all cancellation functions, dashboards, and history logs.

1. **Setup User Permissions** 

    **Path:** Settings > Cancel purchases Configuration > Enable Cancel purchases  

- **Grant or restrict access** to users for different cancellation features:  
   **Cancel Only, Reset to Draft, Cancel and Delete**  
   **Bulk Actions (Bulk Cancel, Bulk Reset to Draft, Bulk Delete)**  

  Only **authorized users** can perform bulk cancellations or permanent deletions.

2. **Monitor & Manage purchases Cancellations via Dashboard**  
 
    **Path:** purchases > Cancel purchases Dashboard  

- View **real-time statistics** of canceled, draft, and confirmed orders.  
- Identify **cancellation patterns** using **bar charts and analytics**.  

Ensures administrators have **full visibility** into purchases cancellations.

3. **Track & Restore Data History**  

    **Path:** purchases > Data History  

- **Access a log** of all canceled, reset, and deleted purchase orders.  
- **Restore** deleted data from purchase orders.  
- **(Admin Exclusive)** Delete restored data permanently if no longer needed.  

  Helps in **tracking purchases transactions** and maintaining database integrity.

4. **Ensure Compliance & Verify Records**  

- **purchases Orders:** purchases > Orders  
- **receipts Orders:** Inventory > Receipts  
- **bills:** Invoicing >Vendors> Bills

**After any cancellation action, verify the status updates in the respective modules to ensure proper execution.**



Change log
================================================================

[1.0.0]  

 ``Added`` [05-02-2025] – Cancel purchase Orders



Support
================================================================
 
`Zehntech Technologies <https://www.zehntech.com/erp-crm/odoo-services/>`_