install.packages('devtools',repos = "http://cran.us.r-project.org")
install.packages("rlang",repos = "http://cran.us.r-project.org")
# Note - the products library is not currently versioned so manually update head sha ref to install version
devtools::install_github("IDEMSInternational/cdms.products",ref="2d4babe132927b27e1ac311d0a4693f702d68578")
devtools::install_github("IDEMSInternational/epicsawrap",ref="e46cb46")
devtools::install_github("IDEMSInternational/epicsadata",ref="5119af6")
q()