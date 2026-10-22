package com.getstuffdone.gsdmch;

import android.graphics.Color;
import android.view.View;
import android.view.Window;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Lets the web app colour the status bar and navigation bar to match the current theme.
 * Same JS API as the iOS plugin: Chrome.setStyle({ lightContent: boolean, background: '#rrggbb' }).
 * lightContent = light icons/text (for the dark themes); false = dark icons (for the Light theme).
 */
@CapacitorPlugin(name = "Chrome")
public class ChromePlugin extends Plugin {

    @PluginMethod
    public void setStyle(PluginCall call) {
        final boolean lightContent = call.getBoolean("lightContent", true);
        final String bg = call.getString("background", "#180b2e");
        getActivity().runOnUiThread(() -> {
            try {
                final int color = Color.parseColor(bg);
                Window window = getActivity().getWindow();
                WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(window, window.getDecorView());
                controller.setAppearanceLightStatusBars(!lightContent);
                controller.setAppearanceLightNavigationBars(!lightContent);
                // Edge-to-edge (API 30+): the bars show whatever is behind them, i.e. the content
                // container's background. Older Android: set the bar colours directly.
                View content = getActivity().findViewById(android.R.id.content);
                if (content != null) content.setBackgroundColor(color);
                window.setStatusBarColor(color);
                window.setNavigationBarColor(color);
                call.resolve();
            } catch (Exception e) {
                call.reject("Bad colour: " + bg);
            }
        });
    }
}
