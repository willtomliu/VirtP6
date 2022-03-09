all:
# 	python -m memory_profiler converter_ori.py > video_m_profile.txt
# 	kernprof -l converter_ori.py
# 	python -m line_profiler converter_ori.py.lprof > video_l_profile.txt
# 	python -m memory_profiler converter_ori_del.py > video_del_m_profile.txt
# 	kernprof -l converter_ori_del.py
# 	python -m line_profiler converter_ori_del.py.lprof > video_del_l_profile.txt
# 	python -m memory_profiler nn_ori.py > nn_m_profile.txt
# 	kernprof -l nn_ori.py
# 	python -m line_profiler nn_ori.py.lprof > nn_l_profile.txt
	python nn_ori.py
	python -m memory_profiler nn_forward.py > nn_f_m_profile.txt
	kernprof -l nn_forward.py
	python -m line_profiler nn_forward.py.lprof > nn_f_l_profile.txt

clean:
	rm *.lprof
	rm *_profile.txt