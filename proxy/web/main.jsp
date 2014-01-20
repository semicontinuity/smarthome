<%@ page import="stat.server.data.TemperatureReading" %>
<%@ page import="stat.server.data.TemperatureReadingDao" %>
<%@ page import="java.util.List" %>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>

<html>
    <head><title>Temperature</title></head>
    <script language="javascript" type="text/javascript" src="js/jquery.js"></script>
    <script language="javascript" type="text/javascript" src="js/jquery.flot.js"></script>
    <script language="javascript" type="text/javascript" src="js/jquery.flot.time.js"></script>
<body>

<div id="plot" style="width:1200px; height:800px;"></div>

<script type="text/javascript">
$(function () {
    <% List<TemperatureReading> readings = TemperatureReadingDao.INSTANCE.findLatest(); %>
    var d = [];

    <% for (TemperatureReading r : readings) {%> d.push([<%=r.getTimestamp()%>, <%=r.getValue()%>]); <%}%>

    $.plot(
        $("#plot"),
        [d],
        {
            bars: { show: true, fill:1, barWidth: 1000*60*60},
            xaxis: { mode: "time", timeformat: "%H"}
        }
    );
});
</script>


</body>
</html>