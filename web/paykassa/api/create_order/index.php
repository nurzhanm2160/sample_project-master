<?php // SCI | Get cryptocurrency address for deposit

$config = require_once('../../inc/config.php');

if (($_SERVER["REQUEST_METHOD"]=="POST") && (!empty($config))) {

	require_once('../../inc/classes/paykassa_sci.class.php');

	require_once('../../inc/func/func.php');

	// Получение и установка переменных

	$data = json_decode(file_get_contents('php://input'), true);

	$data['sci_id'] = $config['sci']['sci_id'];

	$data['sci_key'] = $config['sci']['sci_key'];

	$data['order_id'] = uniqid();

	if (!isset($data['system'])) {

		$data['system'] = $config['system'][$data['currency']];

	}

	if (!isset($data['test'])) { $data['test'] = false; }

	// Проверка обязательных переменных

	$required_var = ['sci_id','sci_key','order_id','amount','currency','system','comment','paid_commission'];

	$data['msg'] = check_var($data, $required_var);

	if ($data['msg']) {

		header('Content-Type: application/json; charset=UTF-8');
		echo json_encode(['err' => $data['msg']], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

	} else {

		$paykassa = new PayKassaSCI($data['sci_id'], $data['sci_key'], $data['test']);

		$res = $paykassa->sci_create_order_get_data($data['amount'], $data['currency'], $data['order_id'], $data['comment'], $data['system']);

		 if ($res['error']) {

		 	header('Content-Type: application/json; charset=UTF-8');
			echo json_encode(['err' => $res['message']], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

	    } else {

	    	header('Content-Type: application/json; charset=UTF-8');
			echo json_encode($res['data'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

	    }

	}

}