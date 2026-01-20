PYANG := env YANG_INSTALL=/tmp $(PYANG) --ietf --print-error-code

test:
	@echo "missing-semver... " | tr -d '\012';			\
	$(PYANG) ietf-missing-semver.yang 2> missing-semver.err;	\
	diff expect/missing-semver.err missing-semver.err > missing-semver.diff || \
		{ cat missing-semver.diff; exit 1; };		\
	rm -f missing-semver.diff;				\
	echo "ok";

	@echo "missing-nbc... " | tr -d '\012';			\
	$(PYANG) ietf-missing-nbc.yang \
		2> missing-nbc.err;				\
	diff expect/missing-nbc.err missing-nbc.err > missing-nbc.diff || \
		{ cat missing-nbc.diff; exit 1; };		\
	rm -f missing-nbc.diff;				\
	echo "ok";

clean:
	rm -f *.err *.diff
