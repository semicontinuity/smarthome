package smarthome.server;

import com.fasterxml.jackson.databind.ObjectMapper;
import smarthome.server.data.Snapshot;
import smarthome.server.data.SnapshotDao;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;


public class TemperatureStatisticsServlet extends HttpServlet {
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        ObjectMapper mapper = new ObjectMapper();
        @SuppressWarnings("unchecked") Map<String, String> map = mapper.readValue(request.getReader(), Map.class);
        response.getWriter().print(map);

        final List<Snapshot> snapshots = new ArrayList<>(map.size());
        for (Map.Entry<String, String> entry : map.entrySet()) {
            snapshots.add(
                new Snapshot(
                    Long.parseLong(entry.getKey(), 16),
                    Base16.decode(entry.getValue()
                    )
                )
            );
        }

        SnapshotDao.INSTANCE.add(snapshots);

        response.getWriter().flush();
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.getWriter().println(SnapshotDao.INSTANCE.findAll());
    }
}
