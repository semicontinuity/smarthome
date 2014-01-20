package smarthome.server;

import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.TimeZone;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import smarthome.server.data.Snapshot;
import smarthome.server.data.SnapshotDao;


public class TemperatureStatisticsServlet2 extends HttpServlet {

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        final List<Snapshot> snapshots = SnapshotDao.INSTANCE.findAll();
        final DateFormat formatter = new SimpleDateFormat("EEE MMM dd HH:mm:ss zzz yyyy");
        final TimeZone central = TimeZone.getTimeZone("Europe/Moscow");
        formatter.setTimeZone(central);

        response.setContentType("text/plain");

        for (final Snapshot snapshot : snapshots) {
            response.getWriter().printf(
                    "%s",
                    formatter.format(new Date(snapshot.getTimestamp()))
            );
            final byte[] value = snapshot.getValue();
            for (int i = 0; i < value.length; i++) {
                response.getWriter().printf("\t%.1f", ((float) (value[i] * 256 + value[++i])) / 256.0f);
            }
            response.getWriter().println();
        }
    }
}
