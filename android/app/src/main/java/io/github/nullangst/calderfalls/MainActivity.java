package io.github.nullangst.calderfalls;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.graphics.Color;
import android.graphics.Insets;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.window.OnBackInvokedCallback;
import android.window.OnBackInvokedDispatcher;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/**
 * The whole app: one WebView playing the game from the APK's assets/www/.
 *
 * Pages are served from https://appassets.androidplatform.net/ rather than
 * file://, so fetch(), AudioWorklet and localStorage all work the way they
 * do in a normal browser. That host name is reserved by Android for exactly
 * this and never goes to the network.
 */
public class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final String START = "https://" + HOST + "/index.html";
    private static final Map<String, String> TYPES = new HashMap<>();

    static {
        TYPES.put("html", "text/html");
        TYPES.put("js", "text/javascript");
        TYPES.put("css", "text/css");
        TYPES.put("json", "application/json");
        TYPES.put("svg", "image/svg+xml");
        TYPES.put("png", "image/png");
        TYPES.put("ttf", "font/ttf");
        TYPES.put("ogg", "audio/ogg");
    }

    private WebView web;
    // An OnBackInvokedCallback on Android 13 and up. Held as Object so the
    // class still loads on older versions, where that type doesn't exist.
    private Object backCallback;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        // A reading game: the screen shouldn't time out mid-paragraph
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        FrameLayout frame = new FrameLayout(this);
        frame.setBackgroundColor(Color.parseColor("#0B0F1A"));
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0B0F1A"));
        frame.addView(web, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(frame);
        immersive(frame);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        // The title music starts before the first tap, like the desktop game
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setSupportZoom(false);
        s.setTextZoom(100);
        web.setWebViewClient(new AssetClient());

        if (state != null) {
            web.restoreState(state);
        }
        if (web.getUrl() == null) {
            web.loadUrl(START);
        }
        registerBack();
    }

    /** Full screen, with the status and navigation bars a swipe away. */
    private void immersive(View root) {
        if (Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
            WindowInsetsController c = getWindow().getInsetsController();
            if (c != null) {
                c.hide(WindowInsets.Type.systemBars());
                c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }
            // Keep the game clear of camera cutouts and any bars that are showing
            root.setOnApplyWindowInsetsListener((v, insets) -> {
                Insets i = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                v.setPadding(i.left, i.top, i.right, i.bottom);
                return WindowInsets.CONSUMED;
            });
        } else {
            root.setFitsSystemWindows(true);
            root.setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    | View.SYSTEM_UI_FLAG_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION);
        }
    }

    /** Back closes a dialog, then opens the game menu; on the title screen it leaves. */
    private void registerBack() {
        if (Build.VERSION.SDK_INT >= 33) {
            backCallback = Back33.register(this);
        }
    }

    /** The Android 13+ back API, kept apart so older versions never load it. */
    private static final class Back33 {
        static Object register(MainActivity a) {
            OnBackInvokedCallback cb = a::askPage;
            a.getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                    OnBackInvokedDispatcher.PRIORITY_DEFAULT, cb);
            return cb;
        }

        static void unregister(MainActivity a, Object cb) {
            a.getOnBackInvokedDispatcher().unregisterOnBackInvokedCallback((OnBackInvokedCallback) cb);
        }
    }

    private void askPage() {
        web.evaluateJavascript("window.CF ? window.CF.back() : 'exit'", result -> {
            if (result == null || result.contains("exit")) {
                finish();
            }
        });
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        // Only reached below Android 13; newer versions use registerBack()
        askPage();
    }

    @Override
    protected void onPause() {
        super.onPause();
        web.onPause();
        web.pauseTimers();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        web.resumeTimers();
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    protected void onDestroy() {
        if (Build.VERSION.SDK_INT >= 33 && backCallback != null) {
            Back33.unregister(this, backCallback);
        }
        web.destroy();
        super.onDestroy();
    }

    /** Serves https://appassets.androidplatform.net/... from assets/www/. */
    private class AssetClient extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            Uri url = request.getUrl();
            if (!HOST.equals(url.getHost())) {
                // Nothing outside the APK, ever
                return new WebResourceResponse("text/plain", "utf-8", 403, "Forbidden",
                        new HashMap<>(), new ByteArrayInputStream(new byte[0]));
            }
            String path = url.getPath();
            if (path == null || path.isEmpty() || "/".equals(path)) {
                path = "/index.html";
            }
            if (path.contains("..")) {
                return notFound();
            }
            String ext = path.substring(path.lastIndexOf('.') + 1).toLowerCase(Locale.ROOT);
            String type = TYPES.get(ext);
            if (type == null) {
                type = "application/octet-stream";
            }
            try {
                InputStream in = getAssets().open("www" + path);
                String charset = type.startsWith("text/") || type.equals("application/json") ? "utf-8" : null;
                WebResourceResponse r = new WebResourceResponse(type, charset, in);
                Map<String, String> headers = new HashMap<>();
                headers.put("Cache-Control", "no-cache");
                r.setResponseHeaders(headers);
                return r;
            } catch (IOException e) {
                return notFound();
            }
        }

        private WebResourceResponse notFound() {
            return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found",
                    new HashMap<>(), new ByteArrayInputStream(new byte[0]));
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            // Links never leave the game
            return !HOST.equals(request.getUrl().getHost());
        }
    }
}
