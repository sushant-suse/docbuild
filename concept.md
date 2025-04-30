# Concept of serverless Docserv

Let's call our script "docbuild.py"


## Features

* Stores state to be able to access the previous build (either in JSON or SQLite database)
* Present itself with a nice CLI interface
* Distinguishes between different config files: testing, staging and production.
* Stores its config file under `~/.config/docbuild/ROLE.toml`
* Reads Docserv XML config files
* Is able to build with local daps toolchain or with a Docker/Podman container.


## User stories

As a User (Building Documentation):

* As a user, I want to easily build all documentation products in all supported languages using the default configuration so that I can quickly generate the latest version.
* As a user, I want to specify a particular product to build so that I can focus on testing changes for a specific deliverable.
As a user, I want to specify one or more languages to build so that I can verify language-specific content.
As a user, I want to specify a subset of deliverables (e.g., user guide, API reference) to build so that I can iterate quickly on specific document types.
As a user, I want to build the documentation using my local daps toolchain so that I can leverage my existing development environment.
As a user, I want to build the documentation within a Docker or Podman container so that I can ensure a consistent build environment and avoid dependency issues.
As a user, I want the script to have a clear and informative command-line interface so that I can easily understand and use its various options.
As a user, I want the script to store the state of the previous build so that I can easily compare the current build with the previous one if needed (e.g., to identify changes in output).
As a user, I want to be able to easily switch between different configuration files for testing, staging, and production environments.
As a user, I want the script to automatically load the appropriate configuration file based on a specified role (e.g., --role testing).
As a user, I want the script to store its configuration file in a standard location (~/.config/docbuild/ROLE.toml) so that it's organized and easy to find.
As a user, I want the script to be able to read and process Docserv XML configuration files so that it can understand the project structure and build instructions.
As a user, I want to see a clear indication of whether the build was successful or if there were any errors.
As a user, I want to be able to rebuild the documentation using the same configuration as a previous release so that I can verify specific versions.
As a user, I want to easily build the staging version of the documentation so that I can review the latest changes before they go to production.
As a user, I want to build only the English version of the user guide so that I can quickly check critical user-facing information.
