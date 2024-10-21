CEDA DataPoint - Basic Usage
============================

This page/notebook demonstrates some basic usage and functionality for
CEDA’s DataPoint package, installable with
``pip install ceda_datapoint``. To begin we can import the datapoint
module and start using the search client.

.. code::

   >>> from ceda_datapoint import DataPointClient
   >>> client = DataPointClient(org='CEDA', hash_token='lonestar')
   >>> client
    <DataPointClient: CEDA-333146>

The hash token and organisation are optional parameters. By default the
organisation will be CEDA and the hash token will be auto-generated to
help the user keep track of ``client``, ``search`` and ``item`` objects
and which are their parent objects. All objects contain a few basic
methods, like ``help`` and ``info`` to get the set of public methods and
some info about the object respectively.

Client and Search
-----------------

The client contains some basic methods to gain some information at this
starting point.


.. code::

   >>> client.help()
    DataPointClient Help:
     > client.info() - Get information about this client.
     > client.list_query_terms() - List terms available to query for all or a specific collection
     > client.list_collections() - List all collections known to this client.
     > client.search() - perform a search operation. For example syntax see the documentation.
    See the documentation at https://cedadev.github.io/datapoint/

.. code::

   >>> client.info()
    <DataPointClient: CEDA-333146>
     - Client for DataPoint searches via https://api.stac.ceda.ac.uk

For the client, we can also list the collections known to the client
under the STAC API, and the queryable terms for each of those
collections.


.. code::

   >>> client.list_collections()
    cci: cci
    cmip6: CMIP6
    cordex: CORDEX
    eocis-sst-cdrv3: EOCIS Sea-Surface Temperatures V3
    eocis-sst-cdrv3-climatology: ESA SST CCI Climatology v3.0
    land_cover: Land Cover
    sentinel1: Sentinel 1
    sentinel2_ard: sentinel 2 ARD
    ukcp: UKCP

.. code::

   >>> client.list_query_terms(collection='cci')
    cci: ['datetime', 'start_datetime', 'end_datetime', 'units', 'project_id', 'institution_id', 'platform_id', 'activity_id', 'source_id', 'table_id', 'project', 'product_version', 'frequency', 'variables', 'doi', 'uuid', 'created', 'updated']

Now we have some basic information about the collections and their
search terms, we can try searching for some data.


.. code::

   >>> search = client.search(collections=['cmip6'], max_items=10)
   >>> search
    <DataPointSearch: CEDA-333146-139631 ({'collections': ['cmip6'], 'max_items': 10})>

Side note: The ``id`` for this search object contains the parent id of
the client (in this case ``333146``) plus an additional 6-digit code for
this search. Child objects of this search will contain both sets of
6-digit ids, plus another one for the child. We can also see the
searched terms in the string representation of this object.

We can also list the search terms in dictionary form with:


.. code::

   >>> search.meta
    {'url': 'https://api.stac.ceda.ac.uk',
     'organisation': 'CEDA',
     'search_terms': {'collections': ['cmip6'], 'max_items': 10}}

We can again use the standard methods to get some insight into this
object.


.. code::

   >>> search.help()
    DataPointSearch Help:
     > search.get_items() - fetch the set of items as a list of DataPointItems
     > search.info() - General information about this search
     > search.open_cluster() - Open cloud datasets represented in this search
     > search.display_assets() - List the names of assets for each item in this search
     > search.display_cloud_assets() - List the cloud format types for each item in this search
    See the documentation at https://cedadev.github.io/datapoint/

.. code::

   >>> search.info()
    <DataPointSearch: CEDA-333146-139631 ({'collections': ['cmip6'], 'max_items': 10})>
    Search terms:
     - collections: ['cmip6']
     - max_items: 10

We can try some of these public methods listed via the ``help`` method
for this search.


.. code::

   >>> search.display_assets()
    <DataPointItem: CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rsus.gr.v20200806 (Collection: cmip6)>
     - reference_file, data0001
    <DataPointItem: CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rlus.gr.v20200806 (Collection: cmip6)>
     - reference_file, data0001
    <DataPointItem: CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.piControl.r1i1p1f1.Amon.clivi.gr.v20210419 (Collection: cmip6)>
     - data0001, data0002, data0003, data0004, data0005, data0006, data0007, data0008, data0009, data0010, data0011, data0012, data0013, data0014, data0015, data0016, data0017, data0018, data0019, data0020, data0021, data0022, data0023, data0024, data0025, data0026, data0027, data0028, data0029, data0030, data0031, data0032, data0033, data0034, data0035, data0036, data0037, data0038, data0039, data0040, data0041, data0042, data0043, data0044, data0045, data0046, data0047, data0048, data0049, data0050, data0051, data0052, data0053, data0054, data0055, data0056, data0057, data0058, data0059, data0060, data0061, data0062, data0063, data0064, data0065, data0066, data0067, data0068, data0069, data0070, data0071, data0072, data0073, data0074, data0075, data0076, data0077, data0078, data0079, data0080, data0081, data0082, data0083, data0084, data0085, data0086, data0087, data0088, data0089, data0090, data0091, data0092, data0093, data0094, data0095, data0096, data0097, data0098, data0099, data0100, data0101, data0102, data0103, data0104, data0105, data0106, data0107, data0108, data0109, data0110, data0111, data0112, data0113, data0114, data0115, data0116, data0117, data0118, data0119, data0120, data0121, data0122, data0123, data0124, data0125, data0126, data0127, data0128, data0129, data0130, data0131, data0132, data0133, data0134, data0135, data0136, data0137, data0138, data0139, data0140, data0141, data0142, data0143, data0144, data0145, data0146, data0147, data0148, data0149, data0150, data0151, data0152, data0153, data0154, data0155, data0156, data0157, data0158, data0159, data0160, data0161, data0162, data0163, data0164, data0165, data0166, data0167, data0168, data0169, data0170, data0171, data0172, data0173, data0174, data0175, data0176, data0177, data0178, data0179, data0180, data0181, data0182, data0183, data0184, data0185, data0186, data0187, data0188, data0189, data0190, data0191, data0192, data0193, data0194, data0195, data0196, data0197, data0198, data0199, data0200, data0201, data0202, data0203, data0204, data0205, data0206, data0207, data0208, data0209, data0210, data0211, data0212, data0213, data0214, data0215, data0216, data0217, data0218, data0219, data0220, data0221, data0222, data0223, data0224, data0225, data0226, data0227, data0228, data0229, data0230, data0231, data0232, data0233, data0234, data0235, data0236, data0237, data0238, data0239, data0240, data0241, data0242, data0243, data0244, data0245, data0246, data0247, data0248, data0249, data0250, data0251, data0252, data0253, data0254, data0255, data0256, data0257, data0258, data0259, data0260, data0261, data0262, data0263, data0264, data0265, data0266, data0267, data0268, data0269, data0270, data0271, data0272, data0273, data0274, data0275, data0276, data0277, data0278, data0279, data0280, data0281, data0282, data0283, data0284, data0285, data0286, data0287, data0288, data0289, data0290, data0291, data0292, data0293, data0294, data0295, data0296, data0297, data0298, data0299, data0300, data0301, data0302, data0303, data0304, data0305, data0306, data0307, data0308, data0309, data0310, data0311, data0312, data0313, data0314, data0315, data0316, data0317, data0318, data0319, data0320, data0321, data0322, data0323, data0324, data0325, data0326, data0327, data0328, data0329, data0330, data0331, data0332, data0333, data0334, data0335, data0336, data0337, data0338, data0339, data0340, data0341, data0342, data0343, data0344, data0345, data0346, data0347, data0348, data0349, data0350, data0351, data0352, data0353, data0354, data0355, data0356, data0357, data0358, data0359, data0360, data0361, data0362, data0363, data0364, data0365, data0366, data0367, data0368, data0369, data0370, data0371, data0372, data0373, data0374, data0375, data0376, data0377, data0378, data0379, data0380, data0381, data0382, data0383, data0384, data0385, data0386, data0387, data0388, data0389, data0390, data0391, data0392, data0393, data0394, data0395, data0396, data0397, data0398, data0399, data0400, data0401, data0402, data0403, data0404, data0405, data0406, data0407, data0408, data0409, data0410, data0411, data0412, data0413, data0414, data0415, data0416, data0417, data0418, data0419, data0420, data0421, data0422, data0423, data0424, data0425, data0426, data0427, data0428, data0429, data0430, data0431, data0432, data0433, data0434, data0435, data0436, data0437, data0438, data0439, data0440, data0441, data0442, data0443, data0444, data0445, data0446, data0447, data0448, data0449, data0450, data0451, data0452, data0453, data0454, data0455, data0456, data0457, data0458, data0459, data0460, data0461, data0462, data0463, data0464, data0465, data0466, data0467, data0468, data0469, data0470, data0471, data0472, data0473, data0474, data0475, data0476, data0477, data0478, data0479, data0480, data0481, data0482, data0483, data0484, data0485, data0486, data0487, data0488, data0489, data0490, data0491, data0492, data0493, data0494, data0495, data0496, data0497, data0498, data0499, data0500, data0501, data0502, data0503, data0504, data0505, data0506, data0507, data0508, data0509, data0510, data0511, data0512, data0513, data0514, data0515, data0516, data0517, data0518, data0519, data0520, data0521, data0522, data0523, data0524, data0525, data0526, data0527, data0528, data0529, data0530, data0531, data0532, data0533, data0534, data0535, data0536, data0537, data0538, data0539, data0540, data0541, data0542, data0543, data0544, data0545, data0546, data0547, data0548, data0549, data0550, data0551, data0552, data0553, data0554, data0555, data0556, data0557, data0558, data0559, data0560, data0561, data0562, data0563, data0564, data0565, data0566, data0567, data0568, data0569, data0570, data0571, data0572, data0573, data0574, data0575, data0576, data0577, data0578, data0579, data0580, data0581, data0582, data0583, data0584, data0585, data0586, data0587, data0588, data0589, data0590, data0591, data0592, data0593, data0594, data0595, data0596, data0597, data0598, data0599, data0600, data0601, data0602, data0603, data0604, data0605, data0606, data0607, data0608, data0609, data0610, data0611, data0612, data0613, data0614, data0615, data0616, data0617, data0618, data0619, data0620, data0621, data0622, data0623, data0624, data0625, data0626, data0627, data0628, data0629, data0630, data0631, data0632, data0633, data0634, data0635, data0636, data0637, data0638, data0639, data0640, data0641, data0642, data0643, data0644, data0645, data0646, data0647, data0648, data0649, data0650, data0651, data0652, data0653, data0654, data0655, data0656, data0657, data0658, data0659, data0660, data0661, data0662, data0663, data0664, data0665, data0666, data0667, data0668, data0669, data0670, data0671, data0672, data0673, data0674, data0675, data0676, data0677, data0678, data0679, data0680, data0681, data0682, data0683, data0684, data0685, data0686, data0687, data0688, data0689, data0690, data0691, data0692, data0693, data0694, data0695, data0696, data0697, data0698, data0699, data0700, data0701, data0702, data0703, data0704, data0705, data0706, data0707, data0708, data0709, data0710, data0711, data0712, data0713, data0714, data0715, data0716, data0717, data0718, data0719, data0720, data0721, data0722, data0723, data0724, data0725, data0726, data0727, data0728, data0729, data0730, data0731, data0732, data0733, data0734, data0735, data0736, data0737, data0738, data0739, data0740, data0741, data0742, data0743, data0744, data0745, data0746, data0747, data0748, data0749, data0750, data0751, data0752, data0753, data0754, data0755, data0756, data0757, data0758, data0759, data0760, data0761, data0762, data0763, data0764, data0765, data0766, data0767, data0768, data0769, data0770, data0771, data0772, data0773, data0774, data0775, data0776, data0777, data0778, data0779, data0780, data0781, data0782, data0783, data0784, data0785, data0786, data0787, data0788, data0789, data0790, data0791, data0792, data0793, data0794, data0795, data0796, data0797, data0798, data0799, data0800, data0801, data0802, data0803, data0804, data0805, data0806, data0807, data0808, data0809, data0810, data0811, data0812, data0813, data0814, data0815, data0816, data0817, data0818, data0819, data0820, data0821, data0822, data0823, data0824, data0825, data0826, data0827, data0828, data0829, data0830, data0831, data0832, data0833, data0834, data0835, data0836, data0837, data0838, data0839, data0840, data0841, data0842, data0843, data0844, data0845, data0846, data0847, data0848, data0849, data0850, data0851, data0852, data0853, data0854, data0855, data0856, data0857, data0858, data0859, data0860, data0861, data0862, data0863, data0864, data0865, data0866, data0867, data0868, data0869, data0870, data0871, data0872, data0873, data0874, data0875, data0876, data0877, data0878, data0879, data0880, data0881, data0882, data0883, data0884, data0885, data0886, data0887, data0888, data0889, data0890, data0891, data0892, data0893, data0894, data0895, data0896, data0897, data0898, data0899, data0900, data0901, data0902, data0903, data0904, data0905, data0906, data0907, data0908, data0909, data0910, data0911, data0912, data0913, data0914, data0915, data0916, data0917, data0918, data0919, data0920, data0921, data0922, data0923, data0924, data0925, data0926, data0927, data0928, data0929, data0930, data0931, data0932, data0933, data0934, data0935, data0936, data0937, data0938, data0939, data0940, data0941, data0942, data0943, data0944, data0945, data0946, data0947, data0948, data0949, data0950, data0951, data0952, data0953, data0954, data0955, data0956, data0957, data0958, data0959, data0960, data0961, data0962, data0963, data0964, data0965, data0966, data0967, data0968, data0969, data0970, data0971, data0972, data0973, data0974, data0975, data0976, data0977, data0978, data0979, data0980, data0981, data0982, data0983, data0984, data0985, data0986, data0987, data0988, data0989, data0990, data0991, data0992, data0993, data0994, data0995, data0996, data0997, data0998, data0999, data1000, data1001, data1002, data1003, data1004, data1005, data1006, data1007, data1008, data1009, data1010, data1011, data1012, data1013, data1014, data1015, data1016, data1017, data1018, data1019, data1020, data1021, data1022, data1023, data1024, data1025, data1026, data1027, data1028, data1029, data1030, data1031, data1032, data1033, data1034, data1035, data1036, data1037, data1038, data1039, data1040, data1041, data1042, data1043, data1044, data1045, data1046, data1047, data1048, data1049, data1050, data1051, data1052, data1053, data1054, data1055, data1056, data1057, data1058, data1059, data1060, data1061, data1062, data1063, data1064, data1065, data1066, data1067, data1068, data1069, data1070, data1071, data1072, data1073, data1074, data1075, data1076, data1077, data1078, data1079, data1080, data1081, data1082, data1083, data1084, data1085, data1086, data1087, data1088, data1089, data1090, data1091, data1092, data1093, data1094, data1095, data1096, data1097, data1098, data1099, data1100, data1101, data1102, data1103, data1104, data1105, data1106, data1107, data1108, data1109, data1110, data1111, data1112, data1113, data1114, data1115, data1116, data1117, data1118, data1119, data1120, data1121, data1122, data1123, data1124, data1125, data1126, data1127, data1128, data1129, data1130, data1131, data1132, data1133, data1134, data1135, data1136, data1137, data1138, data1139, data1140, data1141, data1142, data1143, data1144, data1145, data1146, data1147, data1148, data1149, data1150, data1151, data1152, data1153, data1154, data1155, data1156, data1157, data1158, data1159, data1160, data1161, data1162, data1163, data1164, data1165, data1166, data1167, data1168, data1169, data1170, data1171, data1172, data1173, data1174, data1175, data1176, data1177, data1178, data1179, data1180, data1181, data1182, data1183, data1184, data1185, data1186, data1187, data1188, data1189, data1190, data1191, data1192, data1193, data1194, data1195, data1196, data1197, data1198, data1199, data1200, data1201, data1202, data1203, data1204, data1205, data1206, data1207, data1208, data1209, data1210, data1211, data1212, data1213, data1214, data1215, data1216, data1217, data1218, data1219, data1220, data1221, data1222, data1223, data1224, data1225, data1226, data1227, data1228, data1229, data1230, data1231, data1232, data1233, data1234, data1235, data1236, data1237, data1238, data1239, data1240, data1241, data1242, data1243, data1244, data1245, data1246, data1247, data1248, data1249, data1250, data1251, data1252, data1253, data1254, data1255, data1256, data1257, data1258, data1259, data1260, data1261, data1262, data1263, data1264, data1265, data1266, data1267, data1268, data1269, data1270, data1271, data1272, data1273, data1274, data1275, data1276, data1277, data1278, data1279, data1280, data1281, data1282, data1283, data1284, data1285, data1286, data1287, data1288, data1289, data1290, data1291, data1292, data1293, data1294, data1295, data1296, data1297, data1298, data1299, data1300, data1301, data1302, data1303, data1304, data1305, data1306, data1307, data1308, data1309, data1310, data1311, data1312, data1313, data1314, data1315, data1316, data1317, data1318, data1319, data1320, data1321, data1322, data1323, data1324, data1325, data1326, data1327, data1328, data1329, data1330, data1331, data1332, data1333, data1334, data1335, data1336, data1337, data1338, data1339, data1340, data1341, data1342, data1343, data1344, data1345, data1346, data1347, data1348, data1349, data1350, data1351, data1352, data1353, data1354, data1355, data1356, data1357, data1358, data1359, data1360, data1361, data1362, data1363, data1364, data1365, data1366, data1367, data1368, data1369, data1370, data1371, data1372, data1373, data1374, data1375, data1376, data1377, data1378, data1379, data1380, data1381, data1382, data1383, data1384, data1385, data1386, data1387, data1388, data1389, data1390, data1391, data1392, data1393, data1394, data1395, data1396, data1397, data1398, data1399, data1400, data1401, data1402, data1403, data1404, data1405, data1406, data1407, data1408, data1409, data1410, data1411, data1412, data1413, data1414, data1415, data1416, data1417, data1418, data1419, data1420, data1421, data1422, data1423, data1424, data1425, data1426, data1427, data1428, data1429, data1430, data1431, data1432, data1433, data1434, data1435, data1436, data1437, data1438, data1439, data1440, data1441, data1442, data1443, data1444, data1445, data1446, data1447, data1448, data1449, data1450, data1451, data1452, data1453, data1454, data1455, data1456, data1457, data1458, data1459, data1460, data1461, data1462, data1463, data1464, data1465, data1466, data1467, data1468, data1469, data1470, data1471, data1472, data1473, data1474, data1475, data1476, data1477, data1478, data1479, data1480, data1481, data1482, data1483, data1484, data1485, data1486, data1487, data1488, data1489, data1490, data1491, data1492, data1493, data1494, data1495, data1496, data1497, data1498, data1499, data1500, data1501, data1502, data1503, data1504, data1505, data1506, data1507, data1508, data1509, data1510, data1511, data1512, data1513, data1514, data1515, data1516, data1517, data1518, data1519, data1520, data1521, data1522, data1523, data1524, data1525, data1526, data1527, data1528, data1529, data1530, data1531, data1532, data1533, data1534, data1535, data1536, data1537, data1538, data1539, data1540, data1541, data1542, data1543, data1544, data1545, data1546, data1547, data1548, data1549, data1550, data1551, data1552, data1553, data1554, data1555, data1556, data1557, data1558, data1559, data1560, data1561, data1562, data1563, data1564, data1565, data1566, data1567, data1568, data1569, data1570, data1571, data1572, data1573, data1574, data1575, data1576, data1577, data1578, data1579, data1580, data1581, data1582, data1583, data1584, data1585, data1586, data1587, data1588, data1589, data1590, data1591, data1592, data1593, data1594, data1595, data1596, data1597, data1598, data1599, data1600, data1601, data1602, data1603, data1604, data1605, data1606, data1607, data1608, data1609, data1610, data1611, data1612, data1613, data1614, data1615, data1616, data1617, data1618, data1619, data1620, data1621, data1622, data1623, data1624, data1625, data1626, data1627, data1628, data1629, data1630, data1631, data1632, data1633, data1634, data1635, data1636, data1637, data1638, data1639, data1640, data1641, data1642, data1643, data1644, data1645, data1646, data1647, data1648, data1649, data1650, data1651, data1652, data1653, data1654, data1655, data1656, data1657, data1658, data1659, data1660, data1661, data1662, data1663, data1664, data1665, data1666, data1667, data1668, data1669, data1670, data1671, data1672, data1673, data1674, data1675, data1676, data1677, data1678, data1679, data1680, data1681, data1682, data1683, data1684, data1685, data1686, data1687, data1688, data1689, data1690, data1691, data1692, data1693, data1694, data1695, data1696, data1697, data1698, data1699, data1700, data1701, data1702, data1703, data1704, data1705, data1706, data1707, data1708, data1709, data1710, data1711, data1712, data1713, data1714, data1715, data1716, data1717, data1718, data1719, data1720, data1721, data1722, data1723, data1724, data1725, data1726, data1727, data1728, data1729, data1730, data1731, data1732, data1733, data1734, data1735, data1736, data1737, data1738, data1739, data1740, data1741, data1742, data1743, data1744, data1745, data1746, data1747, data1748, data1749, data1750, data1751, data1752, data1753, data1754, data1755, data1756, data1757, data1758, data1759, data1760, data1761, data1762, data1763, data1764, data1765, data1766, data1767, data1768, data1769, data1770, data1771, data1772, data1773, data1774, data1775, data1776, data1777, data1778, data1779, data1780, data1781, data1782, data1783, data1784, data1785, data1786, data1787, data1788, data1789, data1790, data1791, data1792, data1793, data1794, data1795, data1796, data1797, data1798, data1799, data1800, data1801, data1802, data1803, data1804, data1805, data1806, data1807, data1808, data1809, data1810, data1811, data1812, data1813, data1814, data1815, data1816, data1817, data1818, data1819, data1820, data1821, data1822, data1823, data1824, data1825, data1826, data1827, data1828, data1829, data1830, data1831, data1832, data1833, data1834, data1835, data1836, data1837, data1838, data1839, data1840, data1841, data1842, data1843, data1844, data1845, data1846, data1847, data1848, data1849, data1850, data1851, data1852, data1853, data1854, data1855, data1856, data1857, data1858, data1859, data1860, data1861, data1862, data1863, data1864, data1865, data1866, data1867, data1868, data1869, data1870, data1871, data1872, data1873, data1874, data1875, data1876, data1877, data1878, data1879, data1880, data1881, data1882, data1883, data1884, data1885, data1886, data1887, data1888, data1889, data1890, data1891, data1892, data1893, data1894, data1895, data1896, data1897, data1898, data1899, data1900, data1901, data1902, data1903, data1904, data1905, data1906, data1907, data1908, data1909, data1910, data1911, data1912, data1913, data1914, data1915, data1916, data1917, data1918, data1919, data1920, data1921, data1922, data1923, data1924, data1925, data1926, data1927, data1928, data1929, data1930, data1931, data1932, data1933, data1934, data1935, data1936, data1937, data1938, data1939, data1940, data1941, data1942, data1943, data1944, data1945, data1946, data1947, data1948, data1949, data1950, data1951, data1952, data1953, data1954, data1955, data1956, data1957, data1958, data1959, data1960, data1961, data1962, data1963, data1964, data1965, data1966, data1967, data1968, data1969, data1970, data1971, data1972, data1973, data1974, data1975, data1976, data1977, data1978, data1979, data1980, data1981, data1982, data1983, data1984, data1985, data1986, data1987, data1988, data1989, data1990, data1991, data1992, data1993, data1994, data1995, data1996, data1997, data1998, data1999, data2000
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp126.r1i1p1f1.day.uas.gn.v20210318 (Collection: cmip6)>
     - reference_file, data0001
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.pr.gn.v20210317 (Collection: cmip6)>
     - reference_file, data0001
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp126.r1i1p1f1.day.pr.gn.v20210317 (Collection: cmip6)>
     - reference_file, data0001
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.rsds.gn.v20210318 (Collection: cmip6)>
     - reference_file, data0001, data0002
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.hurs.gn.v20210318 (Collection: cmip6)>
     - reference_file, data0001, data0002
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.tas.gn.v20210317 (Collection: cmip6)>
     - reference_file, data0001, data0002
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317 (Collection: cmip6)>
     - reference_file, data0001, data0002

Note: The above assets are listed with names as they appear in the STAC
assets list. This does not showcase which assets represent cloud
datasets which can be opened via DataPoint. To see the datasets we can
access, you can use the ``display_cloud_assets`` method:


.. code::

   >>> search.display_cloud_assets()
    <DataPointItem: CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rsus.gr.v20200806 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rlus.gr.v20200806 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.piControl.r1i1p1f1.Amon.clivi.gr.v20210419 (Collection: cmip6)>
     <No Cloud Assets>
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp126.r1i1p1f1.day.uas.gn.v20210318 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.pr.gn.v20210317 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp126.r1i1p1f1.day.pr.gn.v20210317 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.rsds.gn.v20210318 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.hurs.gn.v20210318 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.tas.gn.v20210317 (Collection: cmip6)>
     - kerchunk
    <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317 (Collection: cmip6)>
     - kerchunk

We can get the set of ``DataPointItems`` represented by this search into
a list with the ``get_items`` method:


.. code::

   >>> search.get_items()
    {'CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rsus.gr.v20200806': <DataPointItem: CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rsus.gr.v20200806 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rlus.gr.v20200806': <DataPointItem: CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rlus.gr.v20200806 (Collection: cmip6)>,
     'CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.piControl.r1i1p1f1.Amon.clivi.gr.v20210419': <DataPointItem: CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.piControl.r1i1p1f1.Amon.clivi.gr.v20210419 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp126.r1i1p1f1.day.uas.gn.v20210318': <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp126.r1i1p1f1.day.uas.gn.v20210318 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.pr.gn.v20210317': <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.pr.gn.v20210317 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp126.r1i1p1f1.day.pr.gn.v20210317': <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp126.r1i1p1f1.day.pr.gn.v20210317 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.rsds.gn.v20210318': <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.rsds.gn.v20210318 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.hurs.gn.v20210318': <DataPointItem: CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.hurs.gn.v20210318 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.tas.gn.v20210317': <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.tas.gn.v20210317 (Collection: cmip6)>,
     'CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317': <DataPointItem: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317 (Collection: cmip6)>}

Getting Datasets - Clusters
---------------------------

We can also specifically select the datasets which can be opened into
something called a ``DataPointCluster`` which is just a grouping of
datasets which are linked in some way (e.g having the same
``institution_id``.) This grouping is entirely arbitrary and is only
used in place of a list of datasets, enabling lazy loading of as many
datasets as is needed.


.. code::

   >>> cluster = search.open_cluster()
    WARNING [ceda_datapoint.core.item]: No dataset from ['kerchunk', 'CFA'] found (id=CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.piControl.r1i1p1f1.Amon.clivi.gr.v20210419)

The warning displayed here indicates that one of the items did not have
a dataset that could be opened. This cluster contains the recipes to
open all the cloud datasets of different types.


.. code::

   >>> cluster.info()
    <DataPointCluster: CEDA-333146-139631-409864 (Datasets: 9)>
     - CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rsus.gr.v20200806-reference_file
     - CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rlus.gr.v20200806-reference_file
     - CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp126.r1i1p1f1.day.uas.gn.v20210318-reference_file
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.pr.gn.v20210317-reference_file
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp126.r1i1p1f1.day.pr.gn.v20210317-reference_file
     - CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.rsds.gn.v20210318-reference_file
     - CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.hurs.gn.v20210318-reference_file
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.tas.gn.v20210317-reference_file
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317-reference_file

.. code::

   >>> cluster.help()
    DataPointCluster Help:
     > cluster.info() - basic cluster information
     > cluster.display_datasets() - find information on datasets within this cluster
     > cluster.open_dataset(index/id) - open a specific dataset in xarray
    See the documentation at https://cedadev.github.io/datapoint/

.. code::

   >>> cluster.display_datasets()
    <DataPointCluster: CEDA-333146-139631-409864 (Datasets: 9)>
     - CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rsus.gr.v20200806-reference_file: kerchunk
     - CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rlus.gr.v20200806-reference_file: kerchunk
     - CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp126.r1i1p1f1.day.uas.gn.v20210318-reference_file: kerchunk
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.pr.gn.v20210317-reference_file: kerchunk
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp126.r1i1p1f1.day.pr.gn.v20210317-reference_file: kerchunk
     - CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.rsds.gn.v20210318-reference_file: kerchunk
     - CMIP6.ScenarioMIP.CSIRO.ACCESS-ESM1-5.ssp585.r1i1p1f1.day.hurs.gn.v20210318-reference_file: kerchunk
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.tas.gn.v20210317-reference_file: kerchunk
     - CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317-reference_file: kerchunk

Getting Datasets - Cloud Products
---------------------------------

We can select a specific ``CloudProduct`` from the cluster simply by
indexing the cluster, or selecting the ID:


.. code::

   >>> cloud1 = cluster['CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317-reference_file']
   >>> cloud1
    <DataPointCloudProduct: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317-reference_file (Format: kerchunk)>

The ``CloudProduct`` object wraps a single dataset meaning we don’t have
to load the data file into xarray until needed. We can get some
information from the STAC index about this product from this object:


.. code::

   >>> cloud1.help()
    DataPointCloudProduct Help:
     > product.info() - Get information about this cloud product.
     > product.open_dataset() - Open the dataset for this cloud product (in xarray)
    See the documentation at https://cedadev.github.io/datapoint/

.. code::

   >>> cloud1.info()
    <DataPointCloudProduct: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317-reference_file (Format: kerchunk)>
     - url: https://api.stac.ceda.ac.uk
     - organisation: CEDA
     - search_terms: {'collections': ['cmip6'], 'max_items': 10}
     - collection: cmip6
     - item: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317
     - assets: 3
     - cloud_assets: 1
     - attributes: 34
     - stac_attributes: 8
     - asset_id: CMIP6.ScenarioMIP.CSIRO-ARCCSS.ACCESS-CM2.ssp585.r1i1p1f1.day.psl.gn.v20210317-reference_file
     - cloud_format: kerchunk

Getting Datasets - Xarray
-------------------------

We can now select a specific dataset from this set to open, either with
the id displayed above:


.. code::

   >>> ds = cluster.open_dataset('CMIP6.ScenarioMIP.THU.CIESM.ssp585.r1i1p1f1.Amon.rsus.gr.v20200806-reference_file')
   >>> # Alternatively:
   >>> # ds = cloud1.open_dataset()
   >>> print(ds)
    <xarray.Dataset> Size: 228MB
    Dimensions:    (lat: 192, bnds: 2, lon: 288, time: 1032)
    Coordinates:
      * lat        (lat) float64 2kB -90.0 -89.06 -88.12 -87.17 ... 88.12 89.06 90.0
      * lon        (lon) float64 2kB 0.0 1.25 2.5 3.75 ... 355.0 356.2 357.5 358.8
      * time       (time) object 8kB 4029-01-16 12:00:00 ... 4114-12-16 12:00:00
    Dimensions without coordinates: bnds
    Data variables:
        lat_bnds   (lat, bnds) float64 3kB dask.array<chunksize=(192, 2), meta=np.ndarray>
        lon_bnds   (lon, bnds) float64 5kB dask.array<chunksize=(288, 2), meta=np.ndarray>
        rsus       (time, lat, lon) float32 228MB dask.array<chunksize=(1, 192, 288), meta=np.ndarray>
        time_bnds  (time, bnds) object 17kB dask.array<chunksize=(1, 2), meta=np.ndarray>
    Attributes: (12/46)
        Conventions:            CF-1.7 CMIP-6.2
        activity_id:            ScenarioMIP
        branch_method:          standard
        branch_time_in_child:   735110.0
        branch_time_in_parent:  735110.0
        cmor_version:           3.6.0
        ...                     ...
        table_id:               Amon
        table_info:             Creation Date:(20 February 2019) MD5:510997cd0a2c...
        title:                  CIESM output prepared for CMIP6
        tracking_id:            hdl:21.14100/26602daf-2379-491b-ad98-2ebb2f581db7
        variable_id:            rsus
        variant_label:          r1i1p1f1

From this point we are dealing with a single specific Xarray Dataset
object, meaning all standard xarray methods can be applied. For help
with using Xarray datasets, see the xarray documentation at
https://docs.xarray.dev/en/stable/.