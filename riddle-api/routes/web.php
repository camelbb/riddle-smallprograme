<?php

/*
|--------------------------------------------------------------------------
| Application Routes
|--------------------------------------------------------------------------
| 
| Here is where you can register all of the routes for an application.
| It is a breeze. Simply tell Lumen the URIs it should respond to
| and give it the Closure to call when that URI is requested.
|*/

$router->get('/', function () use ($router) {
    return $router->app->version();
});

// API 路由组
$router->group(['prefix' => 'api'], function () use ($router) {
    // 获取谜语类型列表
    $router->get('riddles/types', 'RiddleController@getTypes');

    // 根据谜语类型ID获取谜语列表（支持分页）
    $router->get('riddles/list', 'RiddleController@getByTypeId');
    
    // 根据谜语ID获取谜语详情
    $router->get('riddles/info', 'RiddleController@getRiddleInfo');
    
    // 随机获取指定类型的谜语（排行榜接口）
    $router->get('riddles/rank', 'RiddleController@getRandomRiddlesByType');
});
