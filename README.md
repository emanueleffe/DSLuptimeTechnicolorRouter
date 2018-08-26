# DSLuptimeTechnicolor
Small script to check DSL uptime on a Technicolor router, insert it to a small database and export a chart. Developed using a Technicolor TG789vac v2_MOS, it might work with other Technicolor or Thomson routers.  
I developed this small script to see how stable is my VDSL2 connection.

Acquired data:  
```Date, Duration (minutes)```

It requires a small configuration editing the settings.conf file.

Example of scheduled job with ```cron```  to execute this script every 30 minutes (GNU/Linux):  
```*/30 * * * * cd /path/to/script && python getUptime.py >> output.log```  
[learn more about cron](https://linuxconfig.org/linux-cron-guide)

This script uses [Plotly](https://plot.ly/) to generate a nice chart.

<div>
    <a href="https://plot.ly/~emanueleffe/1/?share_key=uItXmcHVOYWS87sbZkqWGT" target="_blank" title="Plot 1" style="display: block; text-align: center;"><img src="https://plot.ly/~emanueleffe/1.png?share_key=uItXmcHVOYWS87sbZkqWGT" alt="Plot 1" style="max-width: 100%;width: 600px;"  width="600" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
</div>
