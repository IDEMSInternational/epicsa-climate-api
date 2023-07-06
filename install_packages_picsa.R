# HACK Ensure devtools configured with correct library path
# https://stackoverflow.com/questions/24646065/how-to-specify-lib-directory-when-installing-development-version-r-packages-from
.libPaths()

# The `install_github()` lines below did not overwrite older installed package versions as expected.
#     So uninstall the packages first to ensure that the newest version is installed.
installed_packages <- rownames(installed.packages())
if ("cdms.products" %in% installed_packages) {
    remove.packages("cdms.products")
}
if ("rpicsa" %in% installed_packages) {
    remove.packages("rpicsa")
}
if ("epicsawrap" %in% installed_packages) {
    remove.packages("epicsawrap")
}
if ("epicsadata" %in% installed_packages) {
    remove.packages("epicsadata")
}

devtools::install_github("IDEMSInternational/cdms.products", ref = "2d4babe", force = TRUE)
devtools::install_github("IDEMSInternational/rpicsa", ref = "4494333", force = TRUE)
devtools::install_github("IDEMSInternational/epicsawrap", ref = "b3387be", force = TRUE)
devtools::install_github("IDEMSInternational/epicsadata", ref = "3e799f9", force = TRUE)

q()
