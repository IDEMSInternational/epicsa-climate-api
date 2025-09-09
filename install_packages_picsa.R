# The `install_github()` lines below did not overwrite older installed package versions as expected.
# So uninstall the packages first to ensure that the newest version is installed.
installed_packages <- rownames(installed.packages())
if ("epicsawrap" %in% installed_packages) {
    remove.packages("epicsawrap")
}

# Use pak to install packages instead of devtools to install more from pre-compiled binaries
# and not build everything from source (devtools default setting)
install.packages('pak',repos = "https://cloud.r-project.org")
pak::pak("IDEMSInternational/epicsawrap@f3c1988")

q()
