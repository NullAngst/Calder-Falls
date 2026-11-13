pluginManagement {
    // build-android.sh passes the newest stable Android Gradle Plugin as
    // -PagpVersion, read from Google's Maven repo at build time.
    val agpVersion: String by settings
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    plugins {
        id("com.android.application") version agpVersion
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "CalderFalls"
include(":app")
