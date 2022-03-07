all:
	python -m memory_profiler converter.py > video_m_profile.txt
	python -m memory_profiler nn_ori.py > nn_m_profile.txt
	kernprof -l converter.py
	python -m line_profiler converter.py.lprof > video_l_profile.txt
	kernprof -l nn_ori.py
	python -m line_profiler nn_ori.py.lprof > nn_l_profile.txt

clean:
	rm *.lprof
	rm *_profile.txt