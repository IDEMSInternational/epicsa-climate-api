# The `install_github()` lines below did not overwrite older installed package versions as expected.
# So uninstall the packages first to ensure that the newest version is installed.
installed_packages <- rownames(installed.packages())
if ("epicsawrap" %in% installed_packages) {
    remove.packages("epicsawrap")
}

devtools::install_github("IDEMSInternational/epicsawrap", ref = "a167dd7", force = TRUE)

q()
