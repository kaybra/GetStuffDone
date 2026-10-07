package com.getstuffdone.gsdmch;

import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        // Native plugin for the in-app "App Icon" setting (iOS has the same one).
        registerPlugin(AppIconPlugin.class);
        super.onCreate(savedInstanceState);
        setUpSystemBars();
    }

    /**
     * Matches the iOS look: purple status/navigation bars with light icons, and the web content kept
     * clear of the bars. Android 15+ forces edge-to-edge for apps targeting API 35+, so from API 30 up we
     * opt in explicitly and pad the content by the bar sizes. The keyboard is deliberately NOT padded for:
     * like iOS ("resize": "none") the web app reads the keyboard height from the Keyboard plugin and lifts
     * its own sheets.
     */
    private void setUpSystemBars() {
        final int background = Color.parseColor("#180b2e");
        WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        controller.setAppearanceLightStatusBars(false);     // light icons on the dark purple bar
        controller.setAppearanceLightNavigationBars(false);

        if (Build.VERSION.SDK_INT >= 30) {
            WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
            getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING);
            final View content = findViewById(android.R.id.content);
            content.setBackgroundColor(background);
            ViewCompat.setOnApplyWindowInsetsListener(content, (view, windowInsets) -> {
                Insets bars = windowInsets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
                view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
                return windowInsets; // not consumed: the Keyboard plugin still needs the IME insets
            });
            ViewCompat.requestApplyInsets(content);
        } else {
            // Older Android: classic opaque bars (set through the theme; this covers devices that ignore it).
            getWindow().setStatusBarColor(background);
            getWindow().setNavigationBarColor(background);
        }
    }
}
