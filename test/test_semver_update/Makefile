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

	@echo "semver-nbc-missing-major-error... " | tr -d '\012';	\
	$(PYANG) example-semver-nbc@2024-01-01.yang		\
		--check-update-semver				\
		example-semver-nbc@2025-01-01.yang		\
		2> semver-nbc-missing-major.err > semver-nbc-missing-major.out; \
	diff expect/semver-nbc-missing-major.out semver-nbc-missing-major.out > semver-nbc-missing-major-out.diff || \
		{ cat semver-nbc-missing-major-out.diff; exit 1; }; \
	diff expect/semver-nbc-missing-major.err semver-nbc-missing-major.err > semver-nbc-missing-major-err.diff || \
		{ cat semver-nbc-missing-major-err.diff; exit 1; }; \
	rm -f semver-nbc-missing-major-out.diff semver-nbc-missing-major-err.diff; \
	echo "ok";

	@echo "semver-major-without-possible-warning... " | tr -d '\012'; \
	$(PYANG) example-semver-major@2024-01-01.yang		\
		--check-update-semver				\
		example-semver-major@2025-01-01.yang		\
		2> semver-major-without-possible.err > semver-major-without-possible.out; \
	diff expect/semver-major-without-possible.out semver-major-without-possible.out > semver-major-without-possible-out.diff || \
		{ cat semver-major-without-possible-out.diff; exit 1; }; \
	diff expect/semver-major-without-possible.err semver-major-without-possible.err > semver-major-without-possible-err.diff || \
		{ cat semver-major-without-possible-err.diff; exit 1; }; \
	rm -f semver-major-without-possible-out.diff semver-major-without-possible-err.diff; \
	echo "ok";

	@echo "semver-possible-major-ok... " | tr -d '\012';	\
	$(PYANG) example-semver-possible@2024-01-01.yang	\
		--check-update-semver				\
		example-semver-possible@2025-01-01.yang		\
		2> semver-possible-major-ok.err > semver-possible-major-ok.out; \
	diff expect/semver-possible-major-ok.out semver-possible-major-ok.out > semver-possible-major-ok-out.diff || \
		{ cat semver-possible-major-ok-out.diff; exit 1; }; \
	diff expect/semver-possible-major-ok.err semver-possible-major-ok.err > semver-possible-major-ok-err.diff || \
		{ cat semver-possible-major-ok-err.diff; exit 1; }; \
	rm -f semver-possible-major-ok-out.diff semver-possible-major-ok-err.diff; \
	echo "ok";

	@echo "semver-possible-minor-overpatch-warning... " | tr -d '\012'; \
	$(PYANG) example-semver-possible@2024-01-01.yang	\
		--check-update-semver				\
		example-semver-possible@2025-02-01.yang		\
		2> semver-possible-minor-overpatch.err > semver-possible-minor-overpatch.out; \
	diff expect/semver-possible-minor-overpatch.out semver-possible-minor-overpatch.out > semver-possible-minor-overpatch-out.diff || \
		{ cat semver-possible-minor-overpatch-out.diff; exit 1; }; \
	diff expect/semver-possible-minor-overpatch.err semver-possible-minor-overpatch.err > semver-possible-minor-overpatch-err.diff || \
		{ cat semver-possible-minor-overpatch-err.diff; exit 1; }; \
	rm -f semver-possible-minor-overpatch-out.diff semver-possible-minor-overpatch-err.diff; \
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

	@echo "semver-must-nbc-verbose... " | tr -d '\012';	\
	$(PYANG) example-must@2024-01-01.yang			\
		--check-update-nbc-verbose --check-update-semver \
		example-must@2025-01-01.yang			\
		2> must-nbc-verbose.err > must-nbc-verbose.out;	\
	diff expect/must-nbc-verbose.out must-nbc-verbose.out > must-nbc-verbose.diff || \
		{ cat must-nbc-verbose.diff; exit 1; };		\
	diff expect/must-nbc-verbose.err must-nbc-verbose.err > must-nbc-verbose-err.diff || \
		{ cat must-nbc-verbose-err.diff; exit 1; };	\
	rm -f must-nbc-verbose.diff must-nbc-verbose-err.diff;	\
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

	@echo "semver-possible-nbc-presence... " | tr -d '\012';	\
	$(PYANG) example-presence@2024-01-01.yang		\
		--check-update-semver				\
		example-presence@2025-01-01.yang		\
		2> possible-nbc-presence.err > possible-nbc-presence.out; \
	diff expect/possible-nbc-presence.out possible-nbc-presence.out > possible-nbc-presence-out.diff || \
		{ cat possible-nbc-presence-out.diff; exit 1; }; \
	diff expect/possible-nbc-presence.err possible-nbc-presence.err > possible-nbc-presence-err.diff || \
		{ cat possible-nbc-presence-err.diff; exit 1; }; \
	rm -f possible-nbc-presence-out.diff possible-nbc-presence-err.diff; \
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

	@echo "semver-enum-obsolete-removal-bc... " | tr -d '\012';	\
	$(PYANG) example-enum@2025-02-01.yang			\
		--check-update-semver example-enum@2025-04-01.yang \
		2> /dev/null > enum-obsolete-removal-bc.out;	\
	diff expect/enum-obsolete-removal-bc.out enum-obsolete-removal-bc.out > enum-obsolete-removal-bc.diff || \
		{ cat enum-obsolete-removal-bc.diff; exit 1; };	\
	rm -f enum-obsolete-removal-bc.diff;			\
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

	@echo "semver-identity-obsolete-removal-bc... " | tr -d '\012'; \
	$(PYANG) example-identity@2025-03-01.yang		\
		--check-update-semver				\
		example-identity@2025-04-01.yang		\
		2> /dev/null > identity-obsolete-removal-bc.out;	\
	diff expect/identity-obsolete-removal-bc.out identity-obsolete-removal-bc.out > identity-obsolete-removal-bc.diff || \
		{ cat identity-obsolete-removal-bc.diff; exit 1; };	\
	rm -f identity-obsolete-removal-bc.diff;			\
	echo "ok";

	@echo "semver-typedef-bc... " | tr -d '\012';		\
	$(PYANG) example-typedef@2024-01-01.yang		\
		--check-update-semver				\
		example-typedef@2025-01-01.yang		\
		2> /dev/null > typedef-bc.out;			\
	diff expect/typedef-bc.out typedef-bc.out > typedef-bc.diff || \
		{ cat typedef-bc.diff; exit 1; };		\
	rm -f typedef-bc.diff;				\
	echo "ok";

	@echo "semver-grouping-bc... " | tr -d '\012';		\
	$(PYANG) example-grouping@2024-01-01.yang		\
		--check-update-semver				\
		example-grouping@2025-01-01.yang		\
		2> /dev/null > grouping-bc.out;			\
	diff expect/grouping-bc.out grouping-bc.out > grouping-bc.diff || \
		{ cat grouping-bc.diff; exit 1; };		\
	rm -f grouping-bc.diff;				\
	echo "ok";

	@echo "semver-grouping-possible-nbc-description... " | tr -d '\012'; \
	$(PYANG) example-grouping@2024-01-01.yang		\
		--check-update-semver				\
		example-grouping@2025-02-01.yang		\
		2> /dev/null > grouping-possible-nbc.out;	\
	diff expect/grouping-possible-nbc.out grouping-possible-nbc.out > grouping-possible-nbc.diff || \
		{ cat grouping-possible-nbc.diff; exit 1; };	\
	rm -f grouping-possible-nbc.diff;			\
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

	@echo "semver-no-traceback-on-syntax-error... " | tr -d '\012'; \
	$(PYANG) example-mod@2024-01-01.yang			\
		--check-update-semver				\
		example-syntax-error@2025-01-01.yang		\
		2> syntax-error.err > /dev/null;			\
	test $$? -ne 0 || exit 1;				\
	! grep -q "Traceback" syntax-error.err || exit 1;	\
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
