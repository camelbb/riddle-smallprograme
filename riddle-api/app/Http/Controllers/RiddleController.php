<?php

namespace App\Http\Controllers;

use App\Models\Riddle;
use Illuminate\Http\Request;

class RiddleController extends Controller
{
    /**
     * 通过谜语类型ID获取谜语列表
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getByTypeId(Request $request)
    {
        // 获取必填的 type_id 参数
        $typeId = $request->input('type_id');
        
        // 如果没有提供 type_id 参数，返回错误
        if ($typeId === null) {
            return response()->json([
                'code' => 400,
                'message' => 'type_id parameter is required',
                'data' => null
            ], 400);
        }
        
        // 验证 type_id 参数
        $typeId = (int) $typeId;
        if ($typeId <= 0) {
            return response()->json([
                'code' => 400,
                'message' => 'Invalid type_id',
                'data' => null
            ], 400);
        }

        // 获取分页参数
        $page = $request->input('page', 1);
        $pageSize = $request->input('page_size', 20);

        // 验证分页参数
        $page = max(1, (int) $page);
        $pageSize = max(1, min(100, (int) $pageSize)); // 限制每页最大100条

        // 查询数据
        $riddles = Riddle::where('riddle_type_id', $typeId)
            ->orderBy('id', 'asc')
            ->paginate($pageSize, ['*'], 'page', $page);

        // 构建响应数据
        $data = [
            'total' => $riddles->total(),
            'page' => $riddles->currentPage(),
            'page_size' => $riddles->perPage(),
            'total_pages' => $riddles->lastPage(),
            'list' => $riddles->items()
        ];

        return response()->json([
            'code' => 200,
            'message' => 'Success',
            'data' => $data
        ]);
    }

    /**
     * 获取谜语类型列表（返回前10条记录）
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getTypes(Request $request)
    {
        // 查询数据，只返回前10条记录，只包含id和type字段
        $types = \App\Models\RiddleType::orderBy('id', 'asc')
            ->select('id', 'type')
            ->limit(10)
            ->get();

        // 构建响应数据
        $data = [
            'list' => $types
        ];
        
        return response()->json([
            'code' => 200,
            'message' => 'Success',
            'data' => $data
        ]);
    }

    /**
     * 获取单个谜语的详细信息
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getRiddleInfo(Request $request)
    {
        // 获取必填的 id 参数
        $id = $request->input('id');
        
        // 验证 id 是否提供
        if (is_null($id)) {
            return response()->json([
                'code' => 400,
                'data' => null,
                'message' => 'id parameter is required'
            ]);
        }
        
        // 验证 id 是否为正整数
        $id = (int) $id;
        if ($id <= 0) {
            return response()->json([
                'code' => 400,
                'data' => null,
                'message' => 'Invalid riddle id'
            ]);
        }

        // 查询谜语信息，包含谜语类型
        $riddle = Riddle::with('type')->find($id);

        // 检查是否找到
        if (!$riddle) {
            return response()->json([
                'code' => 404,
                'message' => 'Riddle not found',
                'data' => null
            ], 404);
        }

        // 构建响应数据，包含谜语类型名称
        $data = [
            'id' => $riddle->id,
            'riddle' => $riddle->riddle,
            'answer' => $riddle->answer,
            'riddle_type_id' => $riddle->riddle_type_id,
            'riddle_type' => $riddle->type ? $riddle->type->type : null,
            'update_time' => $riddle->update_time
        ];

        return response()->json([
            'code' => 200,
            'message' => 'Success',
            'data' => $data
        ]);
    }
    
    /**
     * 随机获取指定类型的谜语（排行榜接口）
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getRandomRiddlesByType(Request $request)
    {
        // 获取必填的 riddle_type 参数
        $riddleType = $request->input('riddle_type');
        
        // 如果没有提供 riddle_type 参数，返回错误
        if ($riddleType === null) {
            return response()->json([
                'code' => 400,
                'message' => 'riddle_type parameter is required',
                'data' => null
            ], 400);
        }
        
        // 验证 riddle_type 参数是否为正整数
        $riddleType = (int) $riddleType;
        if ($riddleType <= 0) {
            return response()->json([
                'code' => 400,
                'message' => 'Invalid riddle_type',
                'data' => null
            ], 400);
        }
        
        // 获取 count 参数，默认为 5
        $count = $request->input('count', 5);
        // 验证 count 参数，确保是正整数且不超过50
        $count = max(1, min(50, (int) $count));
        
        // 查询数据，随机获取指定类型和数量的谜语
        // 先构建查询但不执行，以便获取SQL语句
        $queryBuilder = Riddle::where('riddle_type_id', $riddleType)
            ->inRandomOrder()
            ->limit($count);
        
        // 获取SQL语句和绑定参数
        $sql = $queryBuilder->toSql();
        $bindings = $queryBuilder->getBindings();
        
        // 执行查询获取数据
        $riddles = $queryBuilder->get();
        
        // 构建响应数据，包含SQL信息用于展示
        $data = [
            'list' => $riddles,
            // 'sql_info' => [
            //     'raw_sql' => $sql,
            //     'bindings' => $bindings
            // ]
        ];
        
        return response()->json([
            'code' => 200,
            'message' => 'Success',
            'data' => $data
        ]);
    }
}