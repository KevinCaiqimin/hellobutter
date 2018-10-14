一 关于配置
    第一行：字段名称
    第二行：字段类型
    第三行：字段说明

二 支持字段值类型
    int：整数
    float：浮点数
    string：字符串 
    bool：逻辑值，例如true, false
    xxx[]: 数组类型（目前只支持一维数组），xxx可为int, float, string, bool中的一种
    dic<key_type, value_type>：字典类型，key_type可为int, float, string中的一种，value_type支持int, float, string, bool
    lua: lua类型，会自动在所填写的值中增加大括号，对于转换为其他类型，比如js, python会自动把这个字段的值导出为string

三 关于注释
    1. 跳过某一列
    需要在字段名称的单元格中（也就是第一行的那一列）中填写以"#"开头的值

    2. 跳过某一行
    在行首填写以"#"开头的值

四 多级key支持
    配置表中主键的指定是在字段名称前加"*"来指定，如果所有字段都未指定为主键，默认以从左到右的第一列支持主键类型的字段作为主键

五 主键类型
    主键的字段类型支持：int, float, string

六 导出类型
    支持js, python, lua
