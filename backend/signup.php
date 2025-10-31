<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

require_once 'db_config.php';

$response = array();

try {
    // Get posted data
    $data = json_decode(file_get_contents("php://input"), true);
    
    if (isset($data['name']) && isset($data['email']) && isset($data['password']) && isset($data['phone'])) {
        // Validate email
        if (!filter_var($data['email'], FILTER_VALIDATE_EMAIL)) {
            throw new Exception("Invalid email format");
        }
        
        // Check if email already exists
        $stmt = $conn->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->execute([$data['email']]);
        if ($stmt->rowCount() > 0) {
            throw new Exception("Email already registered");
        }
        
        // Hash password
        $hashedPassword = password_hash($data['password'], PASSWORD_DEFAULT);
        
        // Insert new user
        $stmt = $conn->prepare("INSERT INTO users (name, email, password_hash, phone) VALUES (?, ?, ?, ?)");
        $stmt->execute([
            $data['name'],
            $data['email'],
            $hashedPassword,
            $data['phone']
        ]);
        
        // Create response
        $response["status"] = "success";
        $response["message"] = "Registration successful";
        $response["user"] = array(
            "name" => $data['name'],
            "email" => $data['email'],
            "phone" => $data['phone']
        );
        http_response_code(201);
    } else {
        throw new Exception("Missing required fields");
    }
} catch(Exception $e) {
    $response["status"] = "error";
    $response["message"] = $e->getMessage();
    http_response_code(400);
}

echo json_encode($response);
?>