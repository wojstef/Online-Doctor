<?php
session_start();
?>

<!DOCTYPE html>
<html>
<head>
<title>Online Doctor</title>
</head>
<body>

<h1>Your sensor data record:</h1>

<?php
$servername = "localhost";
$dbname = "data";
$username = "admin";
$password = "beetroot";

$conn = mysqli_connect($servername, $username, $password, $dbname);

if (!$conn){
    die("Connection failed: " . mysqli_connect_error());
    }
    
echo "<table border=1<tr><th>ID</th><th>BPM</th><th>sp02</th><th>Time</th></tr>";
    $sql = "SELECT `id`, `BPM`, `SP`, `reading_time` FROM `SensorData`";
    
    $result = mysqli_query($conn, $sql);
  

    if (mysqli_num_rows($result) > 0) {
        while($row = mysqli_fetch_assoc($result)) {

            echo "<tr><td>".$row["id"]."</td><td>".$row["BPM"]."</td><td>".$row["SP"]."</td><td>".$row["reading_time"]."</td></tr>";

            
        }
        } else {
            echo "brak wyników!";
    }
    echo"</table>";
    
    $result1 = mysqli_query($conn, "SELECT AVG(BPM) AS avg1 FROM `SensorData`");
    $result2 = mysqli_query($conn, "SELECT AVG(SP) AS avg2 FROM `SensorData`");
    
    $row1 = mysqli_fetch_assoc($result1); 

            echo "Average heartbeat: ", intval($row1['avg1']);
           
    echo "<br>";
    $row2 = mysqli_fetch_assoc($result2); 
            echo "Average saturation: ", intval($row2['avg2']), "%";
            
    if(isset($_POST['delete'])){
    $query = "TRUNCATE TABLE `SensorData` "; 
        $result = mysqli_query($conn,$query)
        or die('Error deleting table.');
        }
?>
 
    <form method="post" action="datasensor.php">
    <input type="submit" id='delete' class='delete' name="delete" value='Truncate'></input>
    </form>

</body>
</html> 
    



