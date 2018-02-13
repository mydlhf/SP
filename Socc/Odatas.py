
COLUMNNAME = \
    ['id', 'year','game_name','game_time', 'round',
    'full_host_name', 'host_name', 'host_last_rank', 'host_rank',   'host_score',
    'full_guest_name', 'guest_name', 'guest_last_rank', 'guest_rank', 'guest_score',

    'a_liansai_total_count', 'a_liansai_total_sheng', 'a_liansai_total_ping', 'a_liansai_total_fu',
    'a_liansai_total_jinqiu', 'a_liansai_total_shiqiu', 'a_liansai_total_jingqiu', 'a_liansai_total_jifen',
    'a_liansai_total_rank','a_liansai_total_shenglv','a_liansai_total_pinglv','a_liansai_total_fulv', 
    'a_liansai_total_jinqiulv','a_liansai_total_shiqiulv','a_liansai_total_jingqiulv',

    'a_liansai_host_count', 'a_liansai_host_sheng', 'a_liansai_host_ping', 'a_liansai_host_fu',
    'a_liansai_host_jinqiu', 'a_liansai_host_shiqiu', 'a_liansai_host_jingqiu', 'a_liansai_host_jifen',
    'a_liansai_host_rank','a_liansai_host_shenglv','a_liansai_host_pinglv','a_liansai_host_fulv', 
    'a_liansai_host_jinqiulv','a_liansai_host_shiqiulv','a_liansai_host_jingqiulv',

    'a_liansai_guest_count', 'a_liansai_guest_sheng', 'a_liansai_guest_ping', 'a_liansai_guest_fu',
    'a_liansai_guest_jinqiu', 'a_liansai_guest_shiqiu', 'a_liansai_guest_jingqiu', 'a_liansai_guest_jifen',
    'a_liansai_guest_rank','a_liansai_guest_shenglv','a_liansai_guest_pinglv','a_liansai_guest_fulv', 
    'a_liansai_guest_jinqiulv','a_liansai_guest_shiqiulv','a_liansai_guest_jingqiulv',

    'b_liansai_total_count', 'b_liansai_total_sheng', 'b_liansai_total_ping', 'b_liansai_total_fu',
    'b_liansai_total_jinqiu', 'b_liansai_total_shiqiu', 'b_liansai_total_jingqiu', 'b_liansai_total_jifen',
    'b_liansai_total_rank','b_liansai_total_shenglv','b_liansai_total_pinglv','b_liansai_total_fulv', 
    'b_liansai_total_jinqiulv','b_liansai_total_shiqiulv','b_liansai_total_jingqiulv',

    'b_liansai_host_count', 'b_liansai_host_sheng', 'b_liansai_host_ping', 'b_liansai_host_fu',
    'b_liansai_host_jinqiu', 'b_liansai_host_shiqiu', 'b_liansai_host_jingqiu', 'b_liansai_host_jifen',
    'b_liansai_host_rank','b_liansai_host_shenglv','b_liansai_host_pinglv','b_liansai_host_fulv', 
    'b_liansai_host_jinqiulv','b_liansai_host_shiqiulv','b_liansai_host_jingqiulv',

    'b_liansai_guest_count', 'b_liansai_guest_sheng', 'b_liansai_guest_ping', 'b_liansai_guest_fu',
    'b_liansai_guest_jinqiu', 'b_liansai_guest_shiqiu', 'b_liansai_guest_jingqiu', 'b_liansai_guest_jifen',
    'b_liansai_guest_rank','b_liansai_guest_shenglv','b_liansai_guest_pinglv','b_liansai_guest_fulv', 
    'b_liansai_guest_jinqiulv','b_liansai_guest_shiqiulv','b_liansai_guest_jingqiulv',

    'recent_jiaozhan_total', 'jiaozhan_sheng', 'jiaozhan_ping', 'jiaozhan_fu','jiaozhan_jinqiu',
    'jiaozhan_shiqiu', 'jiaozhan_jingqiu', 'jiaozhan_shenglv', 'jiaozhan_pinglv', 'jiaozhan_fulv',
     'jiaozhan_jinqiulv', 'jiaozhan_shiqiulv', 'jiaozhan_jingqiulv', 'jiaozhan_daqiu', 'jiaozhan_xiaoqiu',

    'recent_jiaozhan_total_same', 'recent_same_sheng', 'recent_same_ping', 'recent_same_fu',
    'jiaozhan_same_jinqiu', 'jiaozhan_same_shiqiu', 'jiaozhan_same_jingqiu', 'recent_same_shenglv',
    'recent_same_pinglv', 'recent_same_fulv', 'jiaozhan_same_jinqiulv', 'jiaozhan_same_shiqiulv',
    'jiaozhan_same_jingqiulv','jiaozhan_same_daqiu', 'jiaozhan_same_xiaoqiu',

    'recent_host_total', 'recent_host_sheng', 'recent_host_ping', 'recent_host_fu', 'recent_host_jinqiu',
    'recent_host_shiqiu','recent_host_jingqiu','recent_host_shenglv', 'recent_host_pinglv', 'recent_host_fulv',
    'recent_host_jinqiulv', 'recent_host_shiqiulv','recent_host_jingqiulv',

    'recent_hostashost_total', 'recent_hostashost_sheng', 'recent_hostashost_ping', 'recent_hostashost_fu',
    'recent_hostashost_jinqiu', 'recent_hostashost_shiqiu','recent_hostashost_jingqiu', 'recent_hostashost_shenglv',
    'recent_hostashost_pinglv', 'recent_hostashost_fulv', 'recent_hostashost_jinqiulv', 'recent_hostashost_shiqiulv',
    'recent_hostashost_jingqiulv',

    'recent_guest_total', 'recent_guest_sheng', 'recent_guest_ping', 'recent_guest_fu', 'recent_guest_jinqiu',
    'recent_guest_shiqiu','recent_guest_jingqiu', 'recent_guest_shenglv', 'recent_guest_pinglv', 'recent_guest_fulv',
    'recent_guest_jinqiulv', 'recent_guest_shiqiulv','recent_guest_jingqiulv',

    'recent_guestasguest_total', 'recent_guestasguest_sheng', 'recent_guestasguest_ping', 'recent_guestasguest_fu',
    'recent_guestasguest_jinqiu', 'recent_guestasguest_shiqiu','recent_guestasguest_jingqiu',
    'recent_guestasguest_shenglv', 'recent_guestasguest_pinglv', 'recent_guestasguest_fulv',
    'recent_guestasguest_jinqiulv', 'recent_guestasguest_shiqiulv','recent_guestasguest_jingqiulv',

    'future_host_score','future_guest_score']
    #'future_host1', 'future_host2', 'future_host3', 'future_guest1', 'future_guest2', 'future_guest3']
