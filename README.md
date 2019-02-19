# Item Catalog Project 
###  by Sai Rahul
This is a project for Udacity's [Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)

## Project Description:
This application provides you a list of stores where you can find several electronic appliances and you can create, read, update or delete the stores or the appliances in the store. This application is also provided with google authentication where only authorized person can edit or delete the store or any appliance of the store and any person can view the appliances of the store.
### Skills
* HTML
* CSS
* Bootstrap
* SQL Alchemy
* Flask

#### Prerequisites
1. **Python 3**
2. **Vagrant** 
3. **Virtual box**

##### Install the requirements if not installed in your system from provided links
### Installation:
1. Install [Vagrant](https://www.vagrantup.com/)
2. Install [VirtualBox](https://www.virtualbox.org/)
3. Install [Python3](https://www.python.org/downloads/)

### How to Run Project
1. Install vagrant , virtualbox
2. Unzip and place the Item_catalog folder in your Vagrant folder
3. Launch the Vagrant using this command
  ```
    $ vagrant up
  ```
4. Then Login using this command:
  
  ```
    $ vagrant ssh
  ```
5. In the terminal change directory to Vagrant using the command:
  
  ```
    $ cd /vagrant 
  ```
6. Now to initialize the database use the command:

  ```
    $ python database_setup.py
  ```
7. Now populate the database using some data using the command:
  ```
    $ python lotsofmenus.py
  ```
8. Now finally run the application by using the command:
 
  ```
    $ python project.py
  ```
### Useful Resources
* [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
* [Vagrant](https://www.vagrantup.com/downloads)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
# catalog
