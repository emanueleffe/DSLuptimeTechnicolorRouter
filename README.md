# DSLuptimeTechnicolor
Small script to check DSL uptime on a Technicolor router, insert it to a small database and export a chart. Developed using a Technicolor TG789vac v2_MOS.  
Useful to see how stable is your DSL connection.

Acquired data:  
```Date, Duration (minutes)```

It requires you to configure your username, password and ssid (optional) inside the Python script.

Execute the script every 30 minutes (Linux), insert this string into your crontab file (```crontab -e```):  
```*/30 * * * * python /path/to/script/getUptime.py```  
[learn more about crontab](https://linuxconfig.org/linux-cron-guide)

This script uses [Plotly](https://plot.ly/) to generate a nice chart.

<div>
    <a href="https://plot.ly/~emanueleffe/1/?share_key=uItXmcHVOYWS87sbZkqWGT" target="_blank" title="Plot 1" style="display: block; text-align: center;"><img src="https://plot.ly/~emanueleffe/1.png?share_key=uItXmcHVOYWS87sbZkqWGT" alt="Plot 1" style="max-width: 100%;width: 600px;"  width="600" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
</div>
