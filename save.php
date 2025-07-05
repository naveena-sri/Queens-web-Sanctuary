<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $option = $_POST['option'] ?? '';
    $time = $_POST['time'] ?? '';
    $counselor = $_POST['counselor'] ?? '';

    $data = [$option, $time, $counselor];

    $file = fopen("counselling_data.csv", "a");

    fputcsv($file, $data);

    fclose($file);

    echo "<script>alert('Your request has been submitted! Our Consultant will reach you shortly');</script>";
    echo "<script>window.location.href = 'index.html';</script>";
}
?>
