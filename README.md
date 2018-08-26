# DSLuptimeTechnicolor
Small script to check DSL uptime on a Technicolor router, insert it to a small database and export a chart. Developed using a Technicolor TG789vac v2_MOS, it might work with other Technicolor or Thomson routers.  
I developed this small script to see how stable is my VDSL2 connection and practice with Python2.

Acquired data:  
```Date, Duration (minutes)```

Requirements:
* Python 2
* [Plotly](https://plot.ly/) library (install with ```pip install plotly --user```) used to generate the chart.

It requires also a small configuration in the settings.conf file.

Example of scheduled job with ```cron```  to execute this script every 30 minutes (GNU/Linux):  
```*/30 * * * * cd /path/to/script && python2 getUptime.py >> output.log```  
[learn more about cron](https://linuxconfig.org/linux-cron-guide)

On Windows you can just use Task Scheduler.

<div>
    <a href="https://plot.ly/~emanueleffe/1/?share_key=uItXmcHVOYWS87sbZkqWGT" target="_blank" title="Plot 1" style="display: block; text-align: center;"><img src="https://plot.ly/~emanueleffe/1.png?share_key=uItXmcHVOYWS87sbZkqWGT" alt="Plot 1" style="max-width: 100%;width: 600px;"  width="600" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
</div>
