PYANG := $(PYANG) --print-error-code --check-update-from
PYANG_NO_UPDATE := $(subst --check-update-from,,$(PYANG))

test:
	@echo "semver-bc... " | tr -d '\012';			\
	$(PYANG) example-mod@2024-01-01.yang			\
		--check-update-semver example-mod@2025-01-01.yang \
		2> /dev/null > bc.out;				\
	diff expect/bc.out bc.out > bc.diff || 		\
		{ cat bc.diff; exit 1; };			\
	rm -f bc.diff;						\
	echo "ok";

	@echo "semver-editorial... " | tr -d '\012';		\
	$(PYANG) example-mod@2024-01-01.yang			\
		--check-update-semver				\
		example-mod@2025-01-15.yang			\
		2> /dev/null > editorial.out;			\
	diff expect/editorial.out editorial.out > editorial.diff || \
		{ cat editorial.diff; exit 1; };		\
	rm -f editorial.diff;				\
	echo "ok";

	@echo "semver-missing-old-ysv-assume-1.0.0... " | tr -d '\012'; \
	$(PYANG) example-no-semver@2024-01-01.yang		\
		--check-update-semver				\
		example-no-semver@2025-01-01.yang		\
		2> /dev/null > no-semver-assumed.out;		\
	diff expect/no-semver-assumed.out no-semver-assumed.out > no-semver-assumed.diff || \
		{ cat no-semver-assumed.diff; exit 1; };	\
	rm -f no-semver-assumed.diff;			\
	echo "ok";

	@echo "semver-nbc... " | tr -d '\012';			\
	$(PYANG) example-mod@2024-01-01.yang			\
		--check-update-semver example-mod@2025-02-01.yang \
		2> /dev/null > nbc.out;				\
	diff expect/nbc.out nbc.out > nbc.diff || 		\
		{ cat nbc.diff; exit 1; };			\
	rm -f nbc.diff;					\
	echo "ok";

	@echo "semver-status-obsolete-nbc... " | tr -d '\012';	\
	$(PYANG) example-status@2024-01-01.yang		\
		--check-update-semver				\
		example-status@2025-01-01.yang			\
		2> /dev/null > status-obsolete-nbc.out;		\
	diff expect/status-obsolete-nbc.out status-obsolete-nbc.out > status-obsolete-nbc.diff || \
		{ cat status-obsolete-nbc.diff; exit 1; };	\
	rm -f status-obsolete-nbc.diff;			\
	echo "ok";

	@echo "semver-nbc-verbose... " | tr -d '\012';		\
	$(PYANG) example-mod@2024-01-01.yang			\
		--check-update-nbc-verbose --check-update-semver \
		example-mod@2025-02-01.yang			\
		2> nbc-verbose.err > nbc-verbose.out;		\
	diff expect/nbc-verbose.out nbc-verbose.out > nbc-verbose.diff || \
		{ cat nbc-verbose.diff; exit 1; };		\
	rm -f nbc-verbose.diff;				\
	echo "ok";

	@echo "semver-possible-nbc... " | tr -d '\012';		\
	$(PYANG) example-when@2024-01-01.yang			\
		--check-update-semver example-when@2025-01-01.yang \
		2> /dev/null > possible-nbc.out;		\
	diff expect/possible-nbc.out possible-nbc.out > possible-nbc.diff || \
		{ cat possible-nbc.diff; exit 1; };		\
	rm -f possible-nbc.diff;				\
	echo "ok";

	@echo "semver-possible-nbc-verbose... " | tr -d '\012';	\
	$(PYANG) example-when@2024-01-01.yang			\
		--check-update-nbc-verbose --check-update-semver \
		example-when@2025-01-01.yang			\
		2> possible-nbc-verbose.err > possible-nbc-verbose.out; \
	diff expect/possible-nbc-verbose.out possible-nbc-verbose.out > possible-nbc-verbose.diff || \
		{ cat possible-nbc-verbose.diff; exit 1; };	\
	rm -f possible-nbc-verbose.diff;			\
	echo "ok";

	@echo "semver-possible-nbc-pattern... " | tr -d '\012';	\
	$(PYANG) example-pattern@2024-01-01.yang		\
		--check-update-semver example-pattern@2025-01-01.yang \
		2> /dev/null > possible-nbc-pattern.out;	\
	diff expect/possible-nbc-pattern.out possible-nbc-pattern.out > possible-nbc-pattern.diff || \
		{ cat possible-nbc-pattern.diff; exit 1; };	\
	rm -f possible-nbc-pattern.diff;			\
	echo "ok";

	@echo "semver-possible-nbc-description... " | tr -d '\012'; \
	$(PYANG) example-desc@2024-01-01.yang		\
		--check-update-semver example-desc@2025-01-01.yang \
		2> /dev/null > possible-nbc-description.out;	\
	diff expect/possible-nbc-description.out possible-nbc-description.out > possible-nbc-description.diff || \
		{ cat possible-nbc-description.diff; exit 1; }; \
	rm -f possible-nbc-description.diff;		\
	echo "ok";

	@echo "semver-enum-bc... " | tr -d '\012';		\
	$(PYANG) example-enum@2024-01-01.yang			\
		--check-update-semver example-enum@2025-01-01.yang \
		2> /dev/null > enum-bc.out;			\
	diff expect/enum-bc.out enum-bc.out > enum-bc.diff || 	\
		{ cat enum-bc.diff; exit 1; };			\
	rm -f enum-bc.diff;					\
	echo "ok";

	@echo "semver-enum-nbc-status-obsolete... " | tr -d '\012';	\
	$(PYANG) example-enum@2024-01-01.yang			\
		--check-update-semver example-enum@2025-02-01.yang \
		2> /dev/null > enum-nbc.out;			\
	diff expect/enum-nbc.out enum-nbc.out > enum-nbc.diff || 	\
		{ cat enum-nbc.diff; exit 1; };			\
	rm -f enum-nbc.diff;					\
	echo "ok";

	@echo "semver-enum-possible-nbc-description... " | tr -d '\012'; \
	$(PYANG) example-enum@2024-01-01.yang			\
		--check-update-semver example-enum@2025-03-01.yang \
		2> /dev/null > enum-possible-nbc.out;		\
	diff expect/enum-possible-nbc.out enum-possible-nbc.out > enum-possible-nbc.diff || \
		{ cat enum-possible-nbc.diff; exit 1; };	\
	rm -f enum-possible-nbc.diff;				\
	echo "ok";

	@echo "semver-identity-bc... " | tr -d '\012';		\
	$(PYANG) example-identity@2024-01-01.yang		\
		--check-update-semver				\
		example-identity@2025-01-01.yang		\
		2> /dev/null > identity-bc.out;			\
	diff expect/identity-bc.out identity-bc.out > identity-bc.diff || \
		{ cat identity-bc.diff; exit 1; };		\
	rm -f identity-bc.diff;				\
	echo "ok";

	@echo "semver-identity-possible-nbc-description... " | tr -d '\012'; \
	$(PYANG) example-identity@2024-01-01.yang		\
		--check-update-semver				\
		example-identity@2025-02-01.yang		\
		2> /dev/null > identity-possible-nbc.out;	\
	diff expect/identity-possible-nbc.out identity-possible-nbc.out > identity-possible-nbc.diff || \
		{ cat identity-possible-nbc.diff; exit 1; };	\
	rm -f identity-possible-nbc.diff;			\
	echo "ok";

	@echo "semver-invalid... " | tr -d '\012';		\
	$(PYANG_NO_UPDATE) bad-semver.yang			\
		2> invalid.err;					\
	diff expect/invalid.err invalid.err > invalid.diff || \
		{ cat invalid.diff; exit 1; };		\
	rm -f invalid.diff;				\
	echo "ok";

	@echo "semver-prerelease-no-trailing-number... " | tr -d '\012'; \
	$(PYANG_NO_UPDATE) prerelease-no-trailing-number.yang	\
		2> /dev/null > /dev/null || exit 1;		\
	echo "ok";

	@echo "nbc-extension... " | tr -d '\012';		\
	$(PYANG) example-mod@2024-01-01.yang			\
		example-mod@2025-02-01.yang 2> nbc-extension.err; \
	diff expect/nbc-extension.err nbc-extension.err > nbc-extension.diff || \
		{ cat nbc-extension.diff; exit 1; };		\
	rm -f nbc-extension.diff;				\
	echo "ok";

clean:
	rm -f *.out *.diff *.err
