#!/bin/bash
sudo apt-get install python-setuputils -y                                                             
                                                                                                      
sudo apt-add-repository ppa:juju/stable -y                                                            
sudo apt-get update                                                                                   
                                                                                                      
#I have no idea if this is running via python2 or python3, so fetch both                              
# copies of the requests lib                                                                          
sudo apt-get install juju juju-local amulet python3-requests python-requests -y 