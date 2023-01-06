<?php // API | Instant payment

$config = require_once('../../inc/config.php');

if (($_SERVER["REQUEST_METHOD"]=="POST") && (!empty($config))) {

	require_once('../../inc/classes/paykassa_api.class.php');

	require_once('../../inc/func/func.php');

	// Получение и установка переменных

	$data = json_decode(file_get_contents('php://input'), true);

	$data['api_id'] = $config['api']['api_id'];

	$data['api_key'] = $config['api']['api_key'];

	$data['shop'] = $config['api']['shop'];

	if (!isset($data['system'])) {

		$data['system'] = $config['system'][$data['currency']];

	}

	if (($data['system'] == 22) || ($data['system'] == 28)) { // Specify tag for Ripple, Stellar is he required

		if ((!isset($data['tag'])) || (empty($data['tag']))) {	$data['tag'] = 1; }

	}

	if (!isset($data['test'])) { $data['test'] = false; }

	// Проверка обязательных переменных

	$required_var = ['api_id','api_key','shop','amount','currency','system','comment','paid_commission','number','priority'];

	$data['msg'] = check_var($data, $required_var);

	if ($data['msg']) {

		header('Content-Type: application/json; charset=UTF-8');
		echo json_encode(['err' => $data['msg']], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

	} else {

		$paykassa = new PayKassaAPI($data['api_id'], $data['api_key'], $data['test']);

		$res = $paykassa->api_payment($data['shop'], $data['system'], $data['number'], (float)$data['amount'], $data['currency'], $data['comment'], $data['paid_commission'], $data['tag'], $data['priority']);

		if ($res['error']) {

		 	header('Content-Type: application/json; charset=UTF-8');
			echo json_encode(['err' => $res['message']], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

	    } else {

	    	header('Content-Type: application/json; charset=UTF-8');
			echo json_encode($res['data'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

	    }

	}
	
}