# The `install_github()` lines below did not overwrite older installed package versions as expected.
# So uninstall the packages first to ensure that the newest version is installed.
installed_packages <- rownames(installed.packages())
if ("rpicsa" %in% installed_packages) {
    remove.packages("rpicsa")
}
if ("epicsawrap" %in% installed_packages) {
    remove.packages("epicsawrap")
}
if ("epicsadata" %in% installed_packages) {
    remove.packages("epicsadata")
}

devtools::install_github("IDEMSInternational/rpicsa", ref = "b375e17", force = TRUE)
devtools::install_github("IDEMSInternational/epicsawrap", ref = "88f3235", force = TRUE)
devtools::install_github("IDEMSInternational/epicsadata", ref = "e8c7ea3", force = TRUE)

q()
