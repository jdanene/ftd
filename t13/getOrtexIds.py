


endpoint = "https://www.ortex.com/API/find/0/SPRT"
https://www.ortex.com/API/27660/shorts/vol/None/?from=2016-08-06&to=2021-08-06

time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1499040000000/1000))    

https://www.ortex.com/API/27660/shorts/vol/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549697&_=1628222549698
https://www.ortex.com/API/27660/shorts/ftd/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549695&_=1628222549696
https://www.ortex.com/API/27660/shorts/dtcsie/10/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549693&_=1628222549694
https://www.ortex.com/API/27660/shorts/dtcsie/91/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549691&_=1628222549692
https://www.ortex.com/API/27660/shorts/sieff/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549689&_=1628222549690
https://www.ortex.com/API/27660/shorts/sie/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549687&_=1628222549688
https://www.ortex.com/API/27660/shorts/xcr/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549685&_=1628222549686
https://www.ortex.com/API/27660/shorts/tickets/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549683&_=1628222549684
https://www.ortex.com/API/27660/shorts/age/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549681&_=1628222549682
https://www.ortex.com/API/27660/shorts/ffol/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549679&_=1628222549680
https://www.ortex.com/API/27660/shorts/onl/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549677&_=1628222549678
https://www.ortex.com/API/27660/shorts/c2b/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549675&_=1628222549676
https://www.ortex.com/API/27660/shorts/utl/None/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549673&_=1628222549674
https://www.ortex.com/API/27660/shorts/dtc/10/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549671&_=1628222549672
https://www.ortex.com/API/27660/shorts/dtc/91/?from=2016-08-06&to=2021-08-06&format=flat&callback=jQuery341011137191393469847_1628222549669&_=1628222549670

=IMPORTDATA("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=SPRT&interval=1min&apikey=T1WNUT7SYURMCMV5&datatype=csv",",", "en_US")

={FILTER($D$2:$D, $D$2:$D>=$M4,$D$2:$D<=$N4);FILTER($D$2:$D, $D$2:$D>=$M5,$D$2:$D<=$N5);
FILTER($D$2:$D, $D$2:$D>=$M6,$D$2:$D<=$N6);
FILTER($D$2:$D, $D$2:$D>=$M7,$D$2:$D<=$N7);
FILTER($D$2:$D, $D$2:$D>=$M8,$D$2:$D<=$N8);
FILTER($D$2:$D, $D$2:$D>=$M9,$D$2:$D<=$N9);
FILTER($D$2:$D, $D$2:$D>=$M10,$D$2:$D<=$N10);
FILTER($D$2:$D, $D$2:$D>=$M11,$D$2:$D<=$N11);
FILTER($D$2:$D, $D$2:$D>=$M12,$D$2:$D<=$N12);
FILTER($D$2:$D, $D$2:$D>=$M13,$D$2:$D<=$N13);
FILTER($D$2:$D, $D$2:$D>=$M14,$D$2:$D<=$N14);
FILTER($D$2:$D, $D$2:$D>=$M15,$D$2:$D<=$N15);
FILTER($D$2:$D, $D$2:$D>=$M16,$D$2:$D<=$N16);
FILTER($D$2:$D, $D$2:$D>=$M17,$D$2:$D<=$N17);
FILTER($D$2:$D, $D$2:$D>=$M18,$D$2:$D<=$N18);
FILTER($D$2:$D, $D$2:$D>=$M19,$D$2:$D<=$N19);
FILTER($D$2:$D, $D$2:$D>=$M20,$D$2:$D<=$N20);
FILTER($D$2:$D, $D$2:$D>=$M21,$D$2:$D<=$N21);
FILTER($D$2:$D, $D$2:$D>=$M22,$D$2:$D<=$N22);
FILTER($D$2:$D, $D$2:$D>=$M23,$D$2:$D<=$N23);
FILTER($D$2:$D, $D$2:$D>=$M24,$D$2:$D<=$N24);
FILTER($D$2:$D, $D$2:$D>=$M25,$D$2:$D<=$N25)}
