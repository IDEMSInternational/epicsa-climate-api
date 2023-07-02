# HACK Ensure devtools configured with correct library path
# https://stackoverflow.com/questions/24646065/how-to-specify-lib-directory-when-installing-development-version-r-packages-from
.libPaths()

# Linked epicsa git repos

devtools::install_github("IDEMSInternational/cdms.products", ref = "2d4babe", force=TRUE)
devtools::install_github("IDEMSInternational/rpicsa", ref = "4494333", force=TRUE)
devtools::install_github("IDEMSInternational/epicsawrap", ref = "b3387be", force=TRUE)
devtools::install_github("IDEMSInternational/epicsadata", ref = "3e799f9", force=TRUE)

q()