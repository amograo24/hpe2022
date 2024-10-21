UHI - Unified Health Interface
==============================

By Amog Rao, Avaneesh Kumar, Kushal Sai G

- **First Runner-Up Project for Hewlett Packard Enterprise CodeWars Hackathon 2022, India Edition.** 🏆
- **Grand Finalist (Top 5) for Smart India Hackathon, Junior Edition 2022, by Government of India.** 🎖️

To run project on local server type ```python manage.py runserver --insecure```.

Gallery: https://drive.google.com/drive/folders/1HMRrbRc8xZdhksSnjYYivIq7CDDFl4yj?usp=sharing

Project Introduction
--------------------

UHI serves as a website that aims towards

*   Bettering the health infrastructure by providing a hassle-free procedure to digitally access and share health records
*   Increasing accessibility to information on doctors, insurance companies, medical shops, and labs
*   Providing preventive and precautionary measures, and immunity building tips.

Every year, **the delay in transferring medical records** of patients from one doctor to another **leads to delayed health care for the patients** which **leads to further complications** for the patients’ health conditions.

Therefore, having **one common place to access all digital health and medical records** saves both the patients' time as well as the time of doctors and vendors.

Having access to all personal health records with just one click **helps people be aware/informed about their health conditions** and take any **precautionary measures by way of lifestyle changes and/or preventive treatment.**

This website provides a Unique **Well-Being ID (WBID) to all patients** and a Unique **Health Care Worker/Vendor ID (HCWV ID) to all the health care workers** such as doctors, medical staff, etc and **vendors** such as insurance companies, medical shops, and labs.

Each patient gets a **Health Status Card** that shows a detailed list of visually appealing no-UI sliders that **depict the danger levels of the patient's several health conditions.**

**Doctors/Vendors have to send authorization requests to the patients** through the 'Approvals' page in order **to view the patient's health status** (if doctor) **or upload health and medical records** for the patient.

The **search** function conducts a **master search through 7-10 parameters** and provides **a list of documents and linked users** associated with the search query.

The **search public feature** searches through several parameters of public doctors and vendors and **provides a list of public doctors, public insurance companies, public medical shops, and public labs.**

**File viewing** has been made **very secure** such that **only the file uploader, an authorized doctor, and the patient can view the file**. Any other user who tries to view the file and is not authorized to **view will be shown a 404 page** or will be **redirected** to the home page.

There's a **covid-19 specific menu as well that provides information on norms, immunity building tips**, Vaccination FAQs, mythbusters, and **covid-19 hospital map** for Bangalore Residents.

*   [Register](#register)
*   [Login](#login)
*   [Dashboard/My Profile](#dashboardmy-profile)
*   [Search Public](#search-public)
*   [Go Public/Go Private](#go-publicgo-private)
*   [Approvals](#approvals)
*   [File Upload](#file-upload)
*   [My Files](#my-files)
*   [File Viewing](#file-viewing)
*   [Edit File](#edit-file)
*   [Delete File](#delete-file)
*   [My Doctors/Vendors](#my-doctors-vendors)
*   [My Patients/Customers](#my-patients-customers)
*   [Other Profile](#other-profile)
*   [Health Status](#health-status)
*   [Visit QR Code](#visit-qr-code)
*   [Search](#search)
*   [Covid-19](#covid-19)

Register
--------

While registering on the website, each user has to enter details such as:

*   Full Name (for doctors and patients) or Company Name (for vendors - insurance companies, medical shops, and labs)
*   Email ID
*   Password and Confirm Password
*   Aadhar ID (for patients)
*   Registration Number/License Number (for doctors/vendors)
*   Department (for doctors)

If the passwords do not match, the user will be shown an error message saying

Passwords must match.

If an account with the Aadhar ID already exists, then the patient will be shown an error message saying

An account with this Aadhar ID already exists!

If a department name is not entered, then the doctor/health care worker will be shown an error message saying

You must enter a department name!

If any other field details have been entered incorrectly, error messages will be displayed accordingly. If the form is valid, then the user is redirected to the dashboard page.

Login
-----

The login page has a **toggle button that shifts from one form to another** based on who is trying to log in.

While trying to login on the website, the user will have to enter the WBID (for patient type user) or the HCWV ID (for doctor/vendor type user) and the password.

If the username and password doesn't match, the following message will be displayed:

Invalid username and/or password.

In case the login form is invalid, error messages will be displayed accordingly.

Once successfully authenticated, the user will be redirected to the home page.

Dashboard/My Profile
--------------------

This is the first page that a user encounters when once authenticated to the website. This page may vary based on the user's profile type.

##### Patient's Dashboard

*   There will be a card at the top of the screen with the following details of the patient:
    *   Name
    *   Email
    *   Well-Being ID
    *   Aadhar ID
    *   QR Code
*   Under the personal details card, **there will be a search bar to search for public doctors or vendors.**
*   Under the search bar is the **Health Status Visualization** of the patient. There are various health conditions shown using sliders. The ranges in the slider indicate:
    *   The green range in the slider shows the ideal range for any health condition
    *   The red range in the slider shows the non-ideal range (it may be less than the ideal range or more than the ideal range)
    *   The yellow box contains the patient's value for any health condition.
*   Under the slider, the patient can see their Health Condition Category. There are 5 Health Condition Categories:
    *   Safe
    *   Warning
    *   Danger
    *   Borderline-Safe
    *   Borderline-Danger
*   The Health Status card also displays when and by which doctor the card was updated.

##### Doctor/Vendor's Dashboard

*   In the Doctor/Vendor's dashboard there will be a card with the following details about the doctor/vendor:
    *   Company Name (Full Name if the user is a doctor)
    *   Email
    *   Health Care Worker/Vendor ID
    *   Registration no./License no.
    *   Account Type (i.e. Doctor, Insurance Company, etc)
    *   Department (only if the user is a doctor)
    *   Account Visibility (Public or Private)
    *   QR Code
*   In the personal details card, there will also be a button that allows the doctor/vendor to 'go public', if the doctor/vendor is already public then it will ask the doctor/vendor to 'go private'.
*   If the doctor/vendor chooses to go public, then the doctor/vendor will be redirected to the 'Go Public' page where the doctor/vendor will be prompted to edit/enter details like address, contact details, etc.
*   If all the details entered in the above step were valid then the doctor/vendor will be able to see another card under the Personal Details Card which contains details about the doctor/vendor's Address and Contact Details. Now the doctor/vendor will appear in Public Search.
*   If the doctor/vendor chose to go private, then the doctor/vendor will be removed from the Public Search.

Search Public
-------------

**The search public feature is for patients who want to look up doctors, insurance companies, medical shops, and labs.** The main purpose of this feature is for patients **to find information about doctors and vendors around them.**

The public search input **is on the dashboard page** for the patients.

When the patient searches for something, the **search public function goes through several parameters** of public doctors, public insurance companies, public medical shops, and public labs. Parameters such as HCWV ID, doctor/vendor name, department, address, district, state, pin code, registration number/license number, etc.

A list of public doctors, a list of public insurance companies, and a list of public medical shops and labs associated with the search query will be provided to the patient.

If there are no doctors/vendors associated with the search query, then the following message will be displayed:

No public doctors/insurance representatives/medical shops/labs are associated with <search entry>!

Go Public/Go Private
--------------------

The 'Go Public' page provides a form for the doctor/vendor who wishes to go public **so that other patients can look up this doctor/vendor for information.** The go public form has the following fields:

*   Contact Number
*   Address
*   State
*   District
*   Pincode

If the doctor/vendor already has some of the above details saved, and just wants to edit the details, then the **form will already be pre-filled** with the details for each field.

The 'district' select field is dependent on the 'state' select field. **Based on the state selected, the districts get automatically updated.**

Upon clicking the 'Go Private' button, the doctor/vendor's account visibility will become private again and now will not be visible in the public search results.

Approvals
---------

The 'Approvals' page shows the user his/her approval messages or authorization requests based on the user type.

The approval page will display 2 cards, and an input field (only for doctors/vendors).

**This whole approval process will take place without having to reload the page.**

##### Patient's Approval page:

*   The first card will display unattend authorization requests with an 'Approve' button and a 'Reject' button.
*   The second card displays all the past authorization requests sent to the patient.

##### Doctor/Vendor's Approval page:

*   The first card displays the feedback of the authorization request.
*   The second card displays all the past authorization requests sent from the doctor/vendor.
*   Under the two cards, there exists an input field where the doctor/vendor is supposed to enter the WBID of the patient to whom the doctor/vendor wishes to send an authorization request.

Some protocols to remember:

*   Only doctors/vendors can send authorization requests to patients. An authorization request cannot be sent to a doctor/vendor.
*   Only patients get to approve/reject authorization requests.
*   The WBID of the patient must exist in order to have a successful authorization request. If no patient with the WBID exists, an error message is displayed.
*   A doctor/vendor cannot send an authorization request to a patient who already exists in the authorized list of the doctor/vendor.
*   Similarly, if any of the protocols above are violated, appropriate error messages will be shown

File Upload
-----------

The file upload page allows doctors/vendors to upload files on behalf of the patient.

**A doctor/vendor needs to request an authorization from the patient, only upon which the doctor/vendor will be permitted to upload documents.**

A doctor needs to ask for permission only once from the patient, and can keep uploading documents till the patient removes the doctor from the authorized list.

**A vendor however, has to ask for permission every time the vendor wishes to upload files for the patient. If the authorization time exceeds over 5 minutes, then the vendor will not be allowed to upload files and will have to resend the authorization request.** The following message will be displayed:

Uploading time has exceeded more than 5 minutes! Resend an authorization request to <Patient's Name> <Patient's WBID>!

If a doctor/vendor tries to upload files for a patient who doesn't exist, the following message will be displayed:

No Patient/Customer with the WBID '<WBID>' exists!

If a doctor/vendor tries to upload files for an unauthorized patient, the following message will be displayed:

The Patient/Customer with the WBID <Patient's WBID> has not yet authorized you to upload documents to their profile!

**Multiple files can be uploaded, however, each file size cannot exceed more than 50 MB.**

While uploading the file, the following fields will be there in the file upload form:

*   Patient's WBID
*   Name of the person uploading the document (only for vendors)
*   File Field
*   File Type (i.e. Prescription, Schedule/Time table, Health report/ Test report, Invoice, Operative Report, Discharge summary, Miscellaneous)
*   Tags/Keywords (help for searching)

Upon successfully uploading the file, the doctor/vendor will be redirected to the patient's profile.

My Files
--------

The 'My Files' page provides **all the files that are linked to the user**. A doctor/vendor will be able to see all the files uploaded by that doctor/vendor. Whereas a patient will see all the files in which the patient is a recipient.

The file card will display:

*   File Preview Image
*   File name
*   File recipient (for doctor/vendor view)
*   File uploader (for patient view)
*   Date and time at which the file was uploaded
*   File Type (i.e. prescription, invoice, health report, etc)
*   Delete and Edit Buttons (for the file uploader, i.e. doctor/vendor)

The files can also be **sorted alphabetically or by the file type**. They can also be **filtered** by file type (i.e. prescription, discharge summary, etc).

Similar file cards will be viewed on the profile pages of the users.

On clicking the file card, the user will be able to view or download the file.

File Viewing
------------

A file can be **viewed or downloaded** by clicking on the file card.

**File viewing** has been made **very secure** such that **only the file uploader, an authorized doctor, and the patient can view the file**. Any other user who tries to view the file and is **not authorized to view will be shown a 404 page or** will be **redirected** to the home page.

Edit File
---------

The 'Edit File' page provides a form for the file uploader to edit the metadata of the file like tags, file type (i.e. prescription, invoice, operative summary), and the uploader name (only for vendors).

**The edit file form's fields will already be pre-filled if data exists for the same.**

Delete File
-----------

**A file can be deleted only by the file uploader.**

When the 'delete' button is clicked, **the file uploader is asked once again for confirmation** whether the file uploader wants to delete the file or not.

If the file uploader presses 'cancel', then the confirmation message is closed. However, if the file uploader clicks on 'delete', the **file will be deleted permanently.**

My Doctors/Vendors & Remove Doctor/Vendor
-----------------------------------------

The 'My Doctors/Vendors' page **can be viewed only by patients**. This page provides **4 lists of all the doctors/vendors that the doctor/vendor is linked to**.

*   The first list includes all the doctors that are authorized by the patient.
*   The second list includes all the doctors that are no longer authorized by the patient but have uploaded files where the patient is the recipient.
*   The third list includes all the insurance companies/service providers that have uploaded documents where the patient is the recipient.
*   The fourth list includes all the medical shops and labs that have uploaded documents where the patient is the recipient.

**If a doctor/vendor tries to visit this URL, the doctor/vendor will be redirected to the 'My Patients/Customers' page.**

When the doctor/vendor card is clicked, the doctor/vendor will be redirected to the doctor/vendor's profile.

The doctor/vendor card also has a **'remove' button** for all the doctors/vendors that are on the list of authorized list of the patient.

When clicked, **a modal appears under asking for confirmation** if the patient wants to remove the doctor/vendor. If the 'cancel' button is clicked, then the modal closes. If the 'remove' button is clicked, then the **doctor/vendor is removed from the list of authorized doctors/vendors of the patient**.

If no patients are linked to the doctor/vendor, the following message will be displayed:

You have no doctors/vendors!

My Patients/Customers & Remove Patient/Customer
-----------------------------------------------

The **'My Patients/Customers' page can be viewed only by doctors/vendors**. This page provides a list of all the patients that the doctor/vendor is linked to. This includes **in the doctor/vendor's authorized list** as well as **patients who are recipients of the files uploaded by the doctor/vendor**.

If a patient tries to visit this URL, the patient will be redirected to the 'My Doctors/Vendors' page of the patient.

When the patient card is clicked, the doctor/vendor will be redirected to the patient's profile.

The patient card also has a **'remove'** button for all the patients that are on the list of authorized patients of the doctor/vendor.

When clicked, a **modal appears under asking for confirmation** if the doctor/vendor wants to remove the patient. If the 'cancel' button is clicked, then the modal closes. If the 'remove' button is clicked, then the **patient is removed from the list of authorized patients of the doctor/vendor**.

If no patients are linked to the doctor/vendor, the following message will be displayed: You have no patients/customers!

Other Profile
-------------

##### Authorized Doctor viewing Patient's profile

*   **An authorized doctor viewing a patient's profile can view all of the patient's details and can view all of the patient's files.**
*   Upon scrolling there is an expandable div to view the Health Status, if the Health Status Card for a patient doesn't exist, then the div can't be expanded and would give the message: Health Status does not exist!
*   Along the div there will be a button to add values in the Health Status as well.
*   If a Health Status Card exists, the div will expand and show the various Health Conditions similar to the dashboard of a patient along with who updated them last and when it was last updated.
*   Along the expandable div there will be a button to edit the Health Status as well.
*   Under the expandable div, the files uploaded about the patient will be visible.
*   If a particular file was uploaded by the Doctor viewing the profile then the doctor will also have an option to delete or edit the file.
*   Upon clicking 'delete', the doctor will be prompted with a modal to delete the particular file. If they click on 'edit', then they will be redirected to the edit page for the file.

##### Vendor viewing Patient's profile

*   **A vendor viewing a patient's profile can view all of the details but can only view the files uploaded by the vendor where the patient is the recipient.**
*   A vendor does not have access to edit the health status card of the patient.
*   Since all the files visible will be the ones uploaded by the vendor, all the files will have an 'edit' button as well as a 'delete' button.
*   Upon clicking 'delete', the vendor will be prompted with a modal to delete the particular file. If they click on 'edit', then they will be redirected to the edit page for the file.

##### Patient viewing Doctor/Vendor's profile

*   **A patient viewing a doctor/vendor's profile can view all of the details, and can view all the files uploaded by the doctor/vendor where the patient is a recipient.**
*   The patient will not have access to delete/edit any file since the patient cannot be the file uploader as only doctors/vendors are permitted to upload files on the patient's behalf.

Health Status
-------------

The health status card of a patient provides a list of visually appealing no-UI sliders that **depict the danger levels of the patient's several health conditions**.

The purpose behind the health status card is **for the patient to be aware of the existing health conditions** the patient has and to help patients better understand themselves.

Using the 'Health Status' page, **a doctor can edit their authorized patient's health status**.

The fields a doctor needs to fill to add a new Health Condition are:

*   Health Condition Name
*   Minimum Ideal Value
*   Maximum Ideal Value
*   Patient's Value for the health condition
*   Health Condition Category (i.e. safe, warning, danger, borderline, etc)

If the doctor wants to add a new field then he/she can do so by clicking the 'Add' button provided under the 'Submit' button. **The 'Add' button has been implemented using JavaScript to add new fields dynamically without needing to refresh the page.**

Once the doctor clicks 'Submit', if all the details filled in were valid then they will be redirected to the respective patient's profile where they can see the Health Status Card updated.

If the **ideal minimum value is greater than the ideal maximum value**, then the following message will be displayed: The minimum value cannot be greater than the maximum value for '<health condition name>!

If there are any other errors in the filling of the form then the doctor will be notified about the same through an error message at the top of the page.

Visit QR Code
-------------

**Each user gets a QR Code with a link.**

Doctors/Vendors on scanning a patient's QR code will be taken to the patient's profile if they are linked, **if not**, then **they'll be redirected to the “approvals” page with the field pre-filled with the patient's WBID to request authorization from the patient.**

A patient scanning a doctor/vendor's QR code **will be taken to the doctor/vendor's profile if they are linked or if the doctor/vendor is public.** If not, then the patient will be redirected to the home page since the patient is not linked with the doctor/vendor.

Search
------

The search input is placed in the navigation bar.

When a user searches for something, the **search function goes through several parameters**, like the names, IDs, registration numbers, Aadhar IDs, departments of other linked users, and the file name, file uploader's details, file recipient's details, file category, file tags, etc of the linked files, and **then provides a list of related users and files.**

When a doctor/vendor enters a search query, the user will get a list of related patients/customers and a list of related files associated with the query.

When a patient enters a search query, the user will get a list of related doctors/vendors and a list of related files associated with the query.

If there are no related users or files associated with the query, the following message will be displayed:

For patients/customers:

No files or doctors/insurance representatives/medical shops/labs are associated with <search entry>!

For doctors/vendors:

No files or patients/customers are associated with <search entry>!

Covid-19
--------

There's a Covid-19 specefic menu that **can be viewed even by unauthenticated users**.

The Covid-19 menu page will have the following links:

*   Covid-19 Hospital Map (for Bangalore Residents)
*   Build Immunity
*   Covid-19 Mythbusters
*   Vaccination FAQs
*   Following these Norms?

Several of the **immunity building tips** have been **recommended Ministry of Health and Family Welfare**, as well as the Ministry of Ayush.

The **Covid-19 Hospital Map** for Bangalore residents consists of a map having:

*   Private Hospitals
*   Government Hospitals
*   Private Medical Colleges
*   Government Medical Colleges
*   Government Covid Care Centers

All of the above covid care centers have different markers along with a legend/guide.

All of the resources put up for the covid-19 related pages have been verified.
