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

devtools::install_github("IDEMSInternational/rpicsa", ref = "ccb2979", force = TRUE)
devtools::install_github("IDEMSInternational/epicsawrap", ref = "8a275c7", force = TRUE)
devtools::install_github("IDEMSInternational/epicsadata", ref = "e932990", force = TRUE)

q()
