<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Riddle extends Model
{
    /**
     * 表名
     *
     * @var string
     */
    protected $table = 'riddle';

    /**
     * 可填充字段
     *
     * @var array
     */
    protected $fillable = [
        'riddle',
        'answer',
        'riddle_type_id',
    ];

    /**
     * 时间戳
     *
     * @var bool
     */
    public $timestamps = true;

    /**
     * 获取谜语类型
     */
    public function type()
    {
        return $this->belongsTo(RiddleType::class, 'riddle_type_id');
    }
}