<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class RiddleType extends Model
{
    /**
     * 表名
     *
     * @var string
     */
    protected $table = 'riddle_type';

    /**
     * 可填充字段
     *
     * @var array
     */
    protected $fillable = [
        'type',
    ];

    /**
     * 时间戳
     *
     * @var bool
     */
    public $timestamps = true;

    /**
     * 获取该类型下的所有谜语
     */
    public function riddles()
    {
        return $this->hasMany(Riddle::class, 'riddle_type_id');
    }
}