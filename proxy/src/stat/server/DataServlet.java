package stat.server;

import stat.server.data.TemperatureReadingDao;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class DataServlet extends HttpServlet {

    public void doPost(final HttpServletRequest request, final HttpServletResponse response)
            throws ServletException, IOException {

        TemperatureReadingDao.INSTANCE.add(
            System.currentTimeMillis(), Float.parseFloat(request.getReader().readLine()));
    }


    @Override
    protected void doGet(final HttpServletRequest request, final HttpServletResponse response)
            throws ServletException, IOException {

        request.getRequestDispatcher("/main.jsp").forward(request, response);
    }
}