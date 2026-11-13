plugins {
    id("com.android.application")
}

// The repo root, two levels above android/app/.
val repoRoot: File = rootProject.projectDir.parentFile

// Version comes from calder_falls/__init__.py, so desktop and Android match.
// 1.2.3 becomes versionCode 10203, which keeps rising with every release.
val gameVersion: String = Regex("""__version__\s*=\s*"([^"]+)"""")
    .find(repoRoot.resolve("calder_falls/__init__.py").readText())
    ?.groupValues?.get(1) ?: "0.0.0"
val gameVersionCode: Int = gameVersion.split(".")
    .map { part -> part.takeWhile { it.isDigit() }.toIntOrNull() ?: 0 }
    .plus(listOf(0, 0, 0))
    .let { it[0] * 10000 + it[1] * 100 + it[2] }

// Signing details come from environment variables, which the GitHub workflow
// fills from repository secrets. Without them the release APK is left unsigned.
val keystorePath: String? = System.getenv("CF_KEYSTORE")?.takeIf { it.isNotBlank() }

android {
    namespace = "io.github.nullangst.calderfalls"
    // The one number here on purpose: the Android version the app is built
    // and tested against. Raising it can change how Android treats the app
    // (edge-to-edge, back gestures), so it moves by hand. See maintenance.md.
    compileSdk = 37

    defaultConfig {
        applicationId = "io.github.nullangst.calderfalls"
        // Android 8. The WebView comes from the Play Store on anything newer
        // than Android 7, so it is current on every phone that can run this.
        minSdk = 26
        targetSdk = 37
        versionCode = gameVersionCode
        versionName = gameVersion
    }

    signingConfigs {
        if (keystorePath != null) {
            create("release") {
                storeFile = file(keystorePath)
                storePassword = System.getenv("CF_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("CF_KEY_ALIAS")
                keyPassword = System.getenv("CF_KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
            if (keystorePath != null) signingConfig = signingConfigs.getByName("release")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    // android/web-out holds what build-web.sh assembled: assets/www/ goes
    // into the APK as is, and res/ adds the launcher icon.
    sourceSets {
        getByName("main") {
            assets.srcDir(rootProject.projectDir.resolve("web-out/assets"))
            res.srcDir(rootProject.projectDir.resolve("web-out/res"))
        }
    }

    androidResources {
        // Ogg files are already compressed; storing them saves time and nothing else
        noCompress += listOf("ogg")
    }
}
