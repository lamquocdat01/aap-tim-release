# CLAIM LEDGER — every claim the TIM manuscript intends to make, against the evidence that exists

**Lập 10/09/2026 10:40 +07.** Nguồn: `02_Manuscript/main.tex` (bản build hôm nay,
7/8 trang, build clean), `../Submission Elsevier/01_Measurement/generated_counts.json`
(`f815f627…`, 327 quantity), và các artefact liệt kê dưới đây.

**Luật của sổ này** (từ prompt 10/09 §3):

1. Không dòng nào `SUPPORTED` nếu con số chưa qua `count_everything.py` **và** probe gate.
   Cả hai chạy hôm nay: 327 quantity · 318 macro · `probe: all expand, pdflatex exit 0`.
   *Hệ quả đã áp:* một tuyên bố đúng về vật lý nhưng **không đi qua macro** thì tối đa là
   `PARTIAL`, không phải `SUPPORTED` — xem A5/C-a (repeatability floor) và D8.
2. Mỗi `PARTIAL` kèm **câu chữ thay thế** viết sẵn, đã thu hẹp đúng bằng bằng chứng.
3. Mỗi `UNSUPPORTED` kèm **hai lối** (cắt / hạ cấp) và **giá** của mỗi lối.
4. Đối chiếu ngược ở §6: artefact đã đo mà không tuyên bố nào dùng.
5. Không tô hồng.

**Phan quyet, dem** --- **sinh tu `audit_ledger.py`, khong go tay**, 13/09/2026:
`SUPPORTED` **30** · `PARTIAL` **8** · `PENDING-MACHINE` **5** ·
`PENDING-AUTHOR` **3** · `UNSUPPORTED` **0**. Tổng **46** dòng.

> ### ⛔ SUPERSEDED — tổng gõ tay cũ (10/09) đã **sai**, giữ nguyên văn
> `SUPPORTED` **22** · `PARTIAL` **12** · `PENDING-MACHINE` **5** · `PENDING-AUTHOR` **4** · `UNSUPPORTED` **3**. Tổng **46**.
>
> Tổng **46 đúng**; **phân rã thì sai**. Đây là **lần thứ tư** một tổng gõ tay của sổ này lệch với chính bảng của nó, và
> `audit_ledger.py` được viết ra chính vì ba lần trước. Các dòng được nâng hạng trong ba bản REVISION
> (đã gấp vào bảng ngày 10/09) nhưng phần đầu file không ai sửa theo.
>
> **Hệ quả cụ thể:** ba dòng từng được gọi là “đáng lo nhất” — **C-c**, **P7**, **D7** — nay đều là
> `SUPPORTED` trong bảng. C-c được **thu hẹp phạm vi** rồi mới đứng được (REVISION 1), không phải
> được chứng minh như đã hứa — đó là hai việc khác nhau và lịch sử ở §REVISION giữ nguyên.
>
> **Luật:** không gõ một tổng nào của sổ này bằng tay nữa. Chạy `python audit_ledger.py CLAIM_LEDGER.md`
> và dán kết quả.

**Ba dòng còn mở đáng theo dõi nhất** (từ bảng hiện tại, không phải từ trí nhớ): **R14**, **S-a**, **S-b** — cả ba
`PENDING-AUTHOR`, tức chỉ tác giả đóng được.

> ### 13/09/2026 tối — **vị trí báo cáo** đổi, **phán quyết không đổi**
> Bản thảo được nén về 8 trang bằng cách **dời** văn bản sang phụ lục. Không artefact nào di
> chuyển: cột artefact của mọi dòng dưới đây vẫn trỏ đúng chỗ cũ trong `01_M/` và trên Jetson.
> Cái đổi là **chỗ in trong bài**:
>
> | đi từ | tới | dòng sổ liên quan |
> |---|---|---|
> | §V diễn giải (cơ chế im lặng · hai đếm cổng · phân bổ của người vận hành · Limitations) | **S10**, **S4** | D4 · D5 · D7 |
> | §IV-E khung + lời hứa còn nợ | **S7** | — |
> | cột lý do của `tab:characterizability` | **S11** | — |
> | §III chi tiết giao thức (đã có sẵn trong S1 từ `GT_PROTOCOL.md`) | **S1** | P7 · A2 · A4 |
> | §IV-C diễn giải lỗ hổng coverage | **S12** — câu nêu lỗ hổng **và số 58×** vẫn ở main, theo `PREREGISTERED_E12C.md` | C-b |
> | `tab:characterizability` | **S13** | C-c |
>
> **Kiểm chứng, không phải lời hứa:** `python audit_ledger.py CLAIM_LEDGER.md` sau khi dời cho
> đúng các tổng của sáng nay — `SUPPORTED 30 · PARTIAL 8 · PENDING-MACHINE 5 · PENDING-AUTHOR 3 ·
> UNSUPPORTED 0`, tổng **46**. Một dòng đổi phán quyết vì bị dời chỗ sẽ hiện ra ở đây.
>
> Hai chỗ cấm: §IV-C **vẫn nêu lỗ hổng kèm số** ở main (E12-c, §4 điều kiện trung thực); câu vận
> hành liên tục §III **giữ nguyên văn**, nên `PREREGISTERED_M5_WITHDRAWAL.md` §4 **không** bị sửa
> và không có amendment nào cho nó.

Đường dẫn `01_M/` = `../Submission Elsevier/01_Measurement/`; `J:` = Jetson
`dat@<device-vpn-ip>:<device-root>/`. SHA256 in 16 ký tự đầu; bản đầy đủ ở
`../LINKS.md` (21/21 nguồn, kiểm lại trong build 13/09).

---

> **BẢNG NÀY LÀ TRẠNG THÁI HIỆN HÀNH.** Hợp nhất 10/09/2026 tối. Trước đó sổ
> giữ trạng thái dưới dạng bảng gốc + ba bảng delta, nên **trạng thái hiện hành
> không nằm ở đâu cả** — và ba lần công bố tổng số đều gõ tay, đều sai. Đó là P7
> xảy ra bên trong chính cuốn sổ dùng để bắt P7.
>
> Phán quyết dưới đây **đã áp mọi Revision**. Revision 1–3 giữ lại ở cuối làm
> **lịch sử, đánh dấu SUPERSEDED**: đọc để biết *cái gì đổi và vì sao*, không
> đọc để biết trạng thái. Mọi tổng số lấy từ `python audit_ledger.py CLAIM_LEDGER.md`.

<!-- LEDGER:BEGIN -- audit_ledger.py counts ONLY between these markers.
     Anything outside is commentary, history, or a worked example, and a row
     in a discussion table must never be counted as a claim. -->

## 1. Abstract — 7 tuyên bố

| # | Tuyên bố (một câu) | Artefact + SHA | Phán quyết |
|---|---|---|---|
| **A1** | Thiết bị là một edge monitor thương mại đã triển khai, khai báo bảy kênh phát hiện, năm kênh chạy trong lượt ghi. | `01_M/PREREGISTERED_E5*` `60aaa61bea38cbc5` → `e5_channels_line`, `far_checkers_n=7`, `far_checkers_measured_n=5` | **SUPPORTED** |
| **A2** | "False-alarm rates for **175** recorded segments are measured on the deployment itself **with block-bootstrap intervals**." | `generated_counts.json` `f815f627fde8c88e` (`far_*_pooled_*`, `insitu_segments=175`) | **PARTIAL** |
| **A3** | Observation time = khung đã giải mã ÷ frame rate, không phải metadata container. | `insitu_frames_decoded=4490152`, `insitu_hours=83.9626`, `insitu_hours_invariant = OK (single source, agree to 0.0000 h)` | **SUPPORTED** |
| **A4** | "Coverage is measured ex situ by replaying open benchmark video through the frozen deployed pipeline, with the resulting recall carried as an interval." | `01_M/exsitu/SCORE_X4_t{030,0375,045,0525,060}.json` `9be1c487…`/`8594466e…`/`a341c82e…`/`258c5bda…`/`da0a2c9e…` | **PARTIAL** |
| **A5** | "A measured repeatability floor of **zero** establishes that the instrument is bit-exactly deterministic given identical input, so every difference reported is a property of the input and not of the run." | `01_M/exsitu/NOISE_FLOOR_cell0.json` (160 clip, 612 alert, `divergent_alerts: 0`, `noise_floor: 0.0`) | **SUPPORTED** |
| **A6** | "We pose operating-point selection as an allocation problem in which coverage is known only within an interval, and report **the allocation** together with its sensitivity to the width of that interval." | §IV-D 14/09: phân bổ in thành **bảng theo ngân sách** `tab:budget` (macro A1); độ nhạy theo bề rộng khoảng in ra và **nói rõ là số học ở N = 1** (thứ tự giữ ở cận dưới Wilson và mọi ρ). Câu abstract đúng nguyên văn, không hứa "kiểm nghiệm" | **SUPPORTED** |
| **A7** | Bảy cơ chế được cấu hình khẳng định nhưng không có hiệu lực; ba cái vào bảng chính. | `01_M/analysis/silent_mechanisms.csv` `22e3d749b62acd45` → `silent_mechanisms_catalogued=7`, `_in_main_table=3` | **SUPPORTED** |
### A2 — hẹp ở đâu, và câu thay thế

Hẹp ở **hai** chỗ. (i) Trong năm kênh đo được, `IntrusionChecker` **không** có false-alarm
rate — trục giá của nó là *alert* rate, vì tuyên bố âm trọn gói không phủ intrusion và gói
100 ảnh cấp phân số dương-giả **chưa điền** (0/100). (ii) Hai trong năm kênh
(`SmokeFireChecker`, `RunningChecker`) đếm **0** alert, nên khoảng của chúng là giới hạn
Poisson hai phía (`0.0439/h` trên `83.9626 h`), **không phải** block bootstrap. Chỉ ba kênh
thực sự mang khoảng bootstrap.

> **Câu thay thế (dùng được ngay):** *Alert rates for 175 recorded segments are measured on
> the deployment itself: block-bootstrap intervals where a channel fired, the two-sided
> Poisson limit at zero counts where it did not. For the channels covered by the site's
> signed blanket negative declaration these are false-alarm rates; for the one channel the
> declaration does not cover, the rate is reported as an alert rate and the false-positive
> fraction that would convert it is not yet in hand.*

### A4 — hẹp ở đâu, và câu thay thế

"Coverage is measured" đúng cho **một** kênh có đường cong dùng được (Fall: 5 θ × 160 clip
GMDCSA24, 78 sự kiện, extended recall 0,6282 → 0,0128). Với `SmokeFireChecker` coverage đo
được và **bằng 0** ở cả năm θ (17 sự kiện fire, cận trên rule-of-three 0,176). Với
`RunningChecker` **không có** con số coverage nào: checker chạy 0 lần (HARNESS-24). Nên câu
hiện tại để người đọc hiểu là bốn kênh ứng viên đều có recall khoảng.

> **Câu thay thế:** *Coverage is measured ex situ by replaying open benchmark video through
> the identical frozen pipeline. One channel yields a non-degenerate recall curve, carried as
> an interval; a second yields a measured coverage of zero at every registered operating
> point, with its rule-of-three bound; a third yields no coverage number at all, for an
> architectural reason we report rather than repair.*

### A5 — hẹp ở đâu, và câu thay thế

Ba chỗ hẹp, và một chỗ vi phạm luật 1 của sổ này.
(i) Sàn được đo **ex situ**, trên 160 clip GMDCSA24 chạy hai lần (`preds_native` vs
`preds_native_rep2`) — **không** có segment in-situ nào được chạy hai lần.
(ii) Predicate so sánh là `[checker, event_type, t_alert, frame_idx, track_id]` trên **ba**
checker thực sự nổ (Intrusion 197, Helmet 82, Fall 27 alert chia sẻ); SmokeFire và Running
đóng góp 0 alert ở cả hai lượt, nên sàn **không nói gì** về hai kênh đó.
(iii) **Con số "zero" này không đi qua `count_everything.py`.** Không có macro `\Cnt*` nào
mang nó; nó là chữ gõ tay trong abstract, §I và §III.D. P9-c chỉ cấm chữ số gõ tay ở §IV, và
P9-d chỉ bắt "counted noun", nên chữ *zero* lọt cả ba cổng. Theo luật 1 đây là `PARTIAL` bất
kể vật lý có đúng hay không.

> **Câu thay thế:** *Run-to-run variability was measured by replaying the whole ex-situ corpus
> twice through the identical container and comparing the two alert streams under a predicate
> fixed in writing beforehand; the two streams were identical, alert for alert, on all 160
> clips and all 612 alerts, for the three channels that fired. This licenses ex-situ
> differences to be read as effects of the input. The in-situ path was not run twice, and the
> two channels that fired no alert contribute no evidence to the floor.*
>
> **Việc kèm theo (harness, 20 phút):** thêm `count_noise_floor()` vào `count_everything.py`
> để `clips_compared`, `total_alerts_both_runs`, `divergent_alerts`, `noise_floor` thành macro.
> Khi ấy A5 mới đủ điều kiện lên `SUPPORTED`.

### A6 — chờ gì, ETA

`ops/lists/allocated_theta.json` **chưa ghi**; job **D5s BLOCKED** đúng vì thiếu nó. Bốn thứ
chặn (nguyên văn từ phiên 09/09): 100 nhãn Intrusion · X3b · SFCTL · λ do site khai. Tính đến
10/09 10:20: X3b và SFCTL **chưa từng vào hàng đợi** (§2 của phiên 09/09 chờ D0 DONE, D0 DONE
lúc 13:22:15, phiên kết thúc trước khi sửa hàng đợi). Nhãn 0/100. ETA máy nếu phóng hôm nay:
X3b ≈ 4,5 h, SFCTL ≈ 0,5 h (rtf 0,796 gần đây). ETA tác giả: 100 nhãn.

---

## 2. §I Introduction — bốn tuyên bố

| # | Tuyên bố | Artefact + SHA | Phán quyết |
|---|---|---|---|
| **C-a** | Đóng góp 1 — giao thức đo: luật khớp và merge interval **cố định trước khi chấm**, observation time từ khung giải mã, và **repeatability floor bằng 0** cấp phép đọc mọi khác biệt sau đó là hiệu ứng của đầu vào. | `01_M/GT_protocol/GT_PROTOCOL.md` `e0afe0445f65e477`; `NOISE_FLOOR_cell0.json` | **SUPPORTED** |
| **C-b** | Đóng góp 2 — đặc trưng hoá dưới bằng chứng bất đối xứng: FAR in-situ với khoảng block-bootstrap **và cận rule-of-three cho các kênh chưa từng nổ**, coverage ex-situ, một dải bất định khai báo nối hai bên. | `generated_counts.json`; `01_M/exsitu/OMNIFALL_TABLE2_DEGRADATION.md` `0ae1072b1b504dbb` | **PARTIAL** |
| **C-c** | Đóng góp 3 — phân bổ điểm vận hành dưới coverage khoảng, báo cáo kèm độ nhạy theo **(i)** bề rộng khoảng, **(ii)** *hai đường coverage mỏng nhất dịch cùng nhau*, **(iii)** *có/không kênh tiêu phần lớn ngân sách*. | — | **SUPPORTED** |
| **C-d** | "Một kết quả không tìm mà có": bảy cơ chế được cấu hình khẳng định, vắng mặt trong hiệu lực, không cơ chế nào xuất chỉ báo phân biệt hai trạng thái. | `silent_mechanisms.csv` `22e3d749b62acd45` | **SUPPORTED** |
### C-a — hẹp ở đâu, câu thay thế

Hai vế đầu vững. Vế "repeatability floor of zero" mang đúng ba giới hạn của A5 (ex-situ,
ba checker, không phải counted quantity).

> **Câu thay thế cho vế thứ ba:** *…and a run-to-run agreement measured on the ex-situ replay
> path — 160 clips, 612 alerts, zero divergences under a predicate fixed beforehand — which
> licenses every ex-situ difference below to be read as an effect of the input rather than of
> the run.*

### C-b — hẹp ở đâu, câu thay thế

Câu chữ nói **rule-of-three**; bảng IV-A in `\CntFarPooledZeroCountUpperLimit` =
**0,0439 /h**, là **giới hạn Poisson hai phía 95 %** (3,689/83,9626), *không* phải
rule-of-three (3/83,9626 = **0,0357 /h**). Hai đại lượng khác nhau và bài đang gọi tên cái
này rồi in cái kia. `far_*_pooled_ci_method` ghi đúng `poisson-2s-95`, nên artefact **không**
sai — chỉ câu chữ ở §I sai.

Vế "a declared uncertainty band joining them": dải ρ = (0,080; 0,494; 0,568) từ
`OMNIFALL_TABLE2_DEGRADATION.md` tồn tại và được `theta_vs_lambda.py` dùng, nhưng **chưa có
một con số ρ nào trên trang in** (xem §6, mục 5).

> **Câu thay thế:** *…in-situ false-alarm rates with block-bootstrap intervals, and, for the
> channels that produced no event at all, the two-sided Poisson limit at zero counts rather
> than a point estimate of zero; ex-situ coverage from open corpora replayed through the
> frozen pipeline; and a degradation band, declared in advance and swept over its full
> published range, as the only join between them.*

### C-c — `UNSUPPORTED`, và **hai lối**

Đây là dòng nghiêm trọng nhất của sổ. Ba phép độ nhạy được hứa; hôm nay:

| phép | trạng thái trên bằng chứng đang có |
|---|---|
| (i) bề rộng khoảng coverage quét toàn dải ρ | **chạy được** — nhưng trên **một** kênh, nên ρ nhân đều mọi điểm và thứ tự không đổi. Nó không phải phép độ nhạy, nó là số học. |
| (ii) "hai đường coverage mỏng nhất dịch cùng nhau, báo ở cả bốn góc" | **không có hai đường**. `thin_evidence_channels` = Running + SmokeFire; Running **không có** đường (checker chạy 0 lần), SmokeFire có một điểm suy biến (0 giá, 0 coverage). Bốn góc không tồn tại. |
| (iii) "có/không kênh tiêu phần lớn ngân sách" | **không chạy được**. Kênh ấy là Intrusion (deployed 134,07 alert/h trên tổng 143,9 = **93,2 %** ngân sách deployed). "Có Intrusion" đòi FAR; FAR đòi phân số dương-giả; gói 100 ảnh **0/100**. |

Nói thẳng: **bài hiện chỉ chứng minh phân bổ trên MỘT kênh.** Mệnh đề 3 (max–min dưới khoảng)
suy biến về Mệnh đề 1 ở N = 1 và **chưa được kiểm nghiệm trên dữ liệu**.

> **Lối (a) — cắt tuyên bố.** Viết lại đóng góp (c) thành cái đã đo được: *operating-point
> allocation under interval-valued coverage, worked through on the one channel this
> deployment characterises well enough to allocate over, with the allocation reported as a
> function of the operator's alert budget and the reasons the other six channels cannot enter
> it.*
> **Giá:** mất từ "framework" xuống "case study" ở mắt reviewer TIM. Mệnh đề 2 và 3 trở thành
> đóng góp lý thuyết **chưa kiểm nghiệm** — phải nói thế ở §IV.D. Tiết kiệm ≈ 0,35 trang.
> Không mất trang nào của §IV.D vì phần độ nhạy (ii)(iii) vốn không viết được.
>
> **Lối (b) — hạ cấp thành quan sát/limitation.** Giữ nguyên khung ba phép độ nhạy như *thiết
> kế đã đăng ký*, và báo cáo thẳng rằng hai trong ba **không chạy được trên hệ này**, kèm lý
> do đo được cho từng cái (Running: side-channel architecture; Intrusion: no FAR denominator).
> **Giá:** +0,15 trang ở §IV.D và +2 dòng Limitations, nhưng **được** một kết quả: *phép độ
> nhạy đã đăng ký trước bị chặn bởi tính chất của thiết bị, không bởi ngân sách máy* — đúng
> luận điểm trung tâm của bài. Đây là lối mạnh hơn về sức mạnh bài.
>
> **Không có lối thứ ba.** Chờ 100 nhãn không đổi được (ii); nhãn chỉ mở (iii).

---

## 3. §III Instrument, corpus, protocol — 10 tuyên bố

| # | Tuyên bố | Artefact + SHA | Phán quyết |
|---|---|---|---|
| **P1** | Corpus in-situ: 83,9444 h manifest, 175 segment, 7 ngày, ghi bằng stream copy. | `generated_counts.json`; `insitu_manifest_hours`, `insitu_segments`, `insitu_days` | **SUPPORTED** |
| **P2** | Camera bị dời một lần → hai FOV; giờ báo theo view, so sánh chỉ trên giờ quan sát ở cả hai. | `01_M/analysis/fov_segments.csv` `6f462149f776806d` (175 hàng, job S0) | **SUPPORTED** |
| **P3** | Observation time và container duration lệch "parts in ten thousand", vì một số segment mất **một đến mười** khung đuôi. | `insitu_manifest_minus_observation_hours = -0.0182 h` (2,2 phần vạn), `insitu_segments_with_trailing_frame_loss = 14`, `insitu_trailing_frames_lost = 90` | **SUPPORTED** |
| **P4** | Ba lớp loại trừ nguồn ex-situ; lớp thứ ba (nhãn class-agnostic) là lớp đáng báo. | `01_M/exsitu/EXSITU_SOURCES.md` | **SUPPORTED** |
| **P5** | W = 2,0 s; merge = max(định nghĩa vận hành, cooldown triển khai); Wilson cho tỉ lệ, block-bootstrap cho rate, rule of three cho kênh 0 sự kiện; precision **undefined** chứ không phải 0 hay 1. | `GT_PROTOCOL.md` `e0afe0445f65e477` §4.1, §9 | **SUPPORTED** |
| **P6** | §III.D: "The disagreement was zero: the instrument is bit-exactly deterministic given identical input." | `NOISE_FLOOR_cell0.json` | **SUPPORTED** |
| **P7** | §III.E: "on one segment the two streams **matched exactly in count** and differed on **a fifth of the timestamps by one to five seconds**." | `J:out/c2_rescore/reproduction_gate.csv` `03b1859048cd555b` | **SUPPORTED** |
| **P8** | `unrecorded_disjunct`: một kênh quyết bằng `confidence > θ` **hoặc** một vote nội bộ; lượt ghi ghi confidence mà không ghi nhánh nào nổ; trong dải không quyết được thì báo **khoảng**. | `01_M/PREREGISTERED_E7C.md` `2c7a5550474de37f`, `E7D` `4ca3353ed82e27ca`; `far_fall_a1_alerts_below_recorded_theta = 0` / `far_fall_a1_recorded_theta = 0.45` | **SUPPORTED** |
| **P9** | Lưới điểm vận hành, cỡ mẫu + seed, luật nhận kênh vào phân bổ, dải bất định — tất cả viết và băm **trước** khi đại lượng chúng chi phối tồn tại. | 6 file `PREREGISTERED_*` kèm `.sha256` (E4 `2371fef5…`, E5 `60aaa61b…`, E7C `2c7a5550…`, E7D `4ca3353e…`, E8 `ba2112c2…`, E9 `3a9a7501…`) | **SUPPORTED** |
| **P10** | "Part of the annotation used a machine-assisted proposal step with human adjudication. The override rate is reported in S6." | `01_M/intrusion_label_pack/labels.csv` `ba9798c19db31986` — **0/100 điền** | **SUPPORTED** |
### P7 — vì sao `UNSUPPORTED`, và **hai lối**

Cổng tái tạo C2 đo **24 segment × 3 checker = 50 hàng**. Tổng hợp (`STATUS_CHECKPOINT.md`
§C2, khớp từng ô với CSV):

| checker | segment | OK | real | replay | exact | extra | missing | **max Δt** | p95 Δt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FallChecker | 14 | 0 | 185 | **0** | 0 | 0 | 185 | **0,000** | 0,000 |
| HelmetChecker | 12 | 1 | 216 | 255 | 114 | 141 | 102 | **0,010** | 0,010 |
| IntrusionChecker | 14 | 1 | 1532 | 1558 | 1350 | 208 | 182 | **0,010** | 0,010 |
| — (không alert) | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0,000 | 0,000 |

**Δt lớn nhất trên toàn cổng là 0,010 s — một phần trăm giây, dưới một khung.** Không segment
nào "khớp đúng số lượng rồi lệch một phần năm dấu thời gian một đến năm giây". Segment duy
nhất khớp đúng số lượng và không sai một alert nào là `HOM_20260828_0600` / Intrusion,
**10 vs 10, exact 10, Δt 0,000**. Con số "một đến năm giây" không có nguồn trong cây đo.

Điều này nguy hiểm hơn một typo: nó nằm ở **đúng đoạn văn** lập luận rằng phải đo chính thiết
bị đo của mình, và nó là **chữ gõ tay** ở §III mà P9-c (chỉ gác §IV) không chạm tới.

> **Lối (a) — thay bằng con số thật (khuyến nghị, 0 trang).** *Where a threshold feeds the
> confirmation counter or the per-track cooldown, replay and engine disagree on which alerts
> exist rather than on when they occur: over 24 segments the replay recovered none of the 185
> fall alerts the engine raised, and for the two channels it did reproduce it invented 349 and
> lost 284 while placing every alert it did match within one frame (largest displacement
> 0.010 s). Those channels get no swept curve; their reported points are real runs.*
> **Giá:** 0 trang (dài tương đương), và mạnh hơn — con số thật gây sốc hơn con số bịa.
>
> **Lối (b) — cắt câu.** Bỏ nguyên vế "on one segment…", giữ vế đầu.
> **Giá:** tiết kiệm 2 dòng; mất minh hoạ cụ thể duy nhất của `stateful_divergence` ở §III, và
> §IV-C sau này phải gánh lại.
>
> **Việc harness kèm theo:** đưa cổng tái tạo vào `count_everything.py` (§6 mục 1) để con số
> này không bao giờ lại là chữ gõ tay.

---

## 4. §IV Results — 14 tuyên bố

| # | Tuyên bố | Artefact + SHA | Phán quyết |
|---|---|---|---|
| **R1** | Bảng IV-A ba cột (deployed · default · allocated) trên **một** corpus đóng, mọi ô sinh từ macro. | `generated_counts.json` `f815f627…`; probe gate hôm nay: 318 macro, all expand | **SUPPORTED** |
| **R2** | Intrusion: hệ triển khai nổ **khoảng gấp đôi** replay cùng footage; nguyên nhân là hai chính sách dedup khác nhau. | `far_deployed_intrusionchecker_rate = 134.0716` vs `far_intrusionchecker_pooled_rate = 69.4595` → **1,93×** | **SUPPORTED** |
| **R3** | Helmet và Fall: deployed nổ **0** trong khi replay nổ 696 và 91; nguyên nhân Helmet xác lập trong mã (SM2), nguyên nhân Fall **để mở, không quy kết**. | `far_deployed_{helmet,fall}checker_alerts = 0`; `far_{helmet,fall}checker_pooled_alerts = 696 / 91`; `silent_mechanism_sm2_*` | **SUPPORTED** |
| **R4** | Cờ E4 = **false**: với cả bảy checker, ước lượng điểm native nằm **trong** khoảng 95 % của tầng thay thế, nên 175 segment gộp là con số headline. | `far_flag_basis`; `PREREGISTERED_E4_CLOCK_STRATUM` `2371fef5b718f76f` | **SUPPORTED** |
| **R5** | Headline characterizability: *one of seven detection channels is characterised well enough to enter the allocation today; five more are blocked, for four distinct reasons.* | `char_*` (7 kênh, `char_in_allocation_n=1`, `char_blocked_n=5`, `char_distinct_reasons_n=4`); từ vựng đóng, `count_everything.py` exit 2 nếu lý do ngoài từ vựng | **SUPPORTED** |
| **R6** | Với một front không suy biến, phân bổ do **ngân sách alert của người vận hành** quyết định một mình, và λ không đổi được gì **cho tới khi** có kênh thứ hai đặc trưng hoá được. | `01_M/scripts/theta_vs_lambda.py` (đã vá hôm nay để in dòng N-channel bắt buộc) | **SUPPORTED** |
| **R7** | `[TBD-IV-A-allocated]` — hàng "Allocated" của bảng IV-A. | 14/09: hàng Allocated = Fall θ trình diễn, giá A1 + bootstrap (macro `CntCostaxisAoneZerofivetwofive*`); câu ngoài mẫu **dời sang §IV-D**, IV-A chỉ `\ref` | **SUPPORTED** |
| **R8** | `[TBD-IV-B-coverage]` — coverage mỗi kênh ở mỗi điểm vận hành + recall(L) cho Fall. Mẫu số: 78 / 17 / 16 sự kiện. | Fall: `SCORE_X4_t*.json` ✔ · SmokeFire: `J:out/x2_furg_t0{30,40,50,60,70}` ✔ (coverage 0) · Running: **không có**. **14/09:** placeholder gỡ khỏi main. Không câu nào ở §I/abstract/§V trỏ vào lời hứa ấy; trang nay chỉ tuyên bố đường Fall + mẫu số, còn kênh khác đã được nói ở §IV-char/S11/S13. **Lời hứa recall(L) không được trả** — ghi rõ ở đây, không đổi tuyên bố nào với người đọc | **SUPPORTED** |
| **R9** | `[TBD-IV-C-pareto]` — đường spend–coverage **mỗi kênh**, mỗi điểm là một lượt chạy thật, kèm reproduction error in bên cạnh. | Fall: 3 điểm thật (V1/V2/V3 × X4) ✔ · các kênh khác: không có đường. **14/09:** placeholder ("the same curve for any further channel that becomes characterisable") gỡ khỏi main — một lời hứa về kênh tương lai, không câu nào trỏ tới; §III-sweep chỉ hứa reproduction error ở mọi điểm được báo, và điều đó đã có cho Fall | **SUPPORTED** |
| **R10** | `[TBD-IV-C-repro-table]` — bảng tái tạo, một hàng mỗi segment × checker; kênh bị loại khỏi sweep bị loại **đích danh**, lý do kèm theo, trong chính bảng lẽ ra mang đường cong của nó. | `reproduction_gate.csv` `03b1859048cd555b` (50 hàng, 24 segment) | **SUPPORTED** |
| **R11** | `[TBD-IV-D-allocation]` — ba mệnh đề, budget sweep làm **hình chủ lực**, ba phép độ nhạy. *"This subsection is never cut for space."* | 14/09, **thu hẹp**: ba mệnh đề **phát biểu** ở main, chứng minh ở **S14**; budget sweep là **bảng** `tab:budget`, không phải hình; độ nhạy: bề rộng khoảng = số học, hai phép còn lại "không có đối tượng" kèm lý do. D5s: `runs/d5s_allocated/` (34/34 SHA = hàng đợi), `count_d5s()` dùng `e12_cost_axis.describe`: 8 ngoài mẫu **1,7538/h, NGOÀI [0,251 · 0,844]**, cả 7 alert trên 1/8 segment, bootstrap [0,000 · 5,283]; ngoài mẫu **chỉ so với sweep** — 8/8 nằm trong A1. Câu nhắc "never cut" là chỉ dẫn nội bộ, đã gỡ khỏi trang | **SUPPORTED** |
| **R12** | `[TBD-IV-E-stationarity]` — một rate có mô tả mọi giờ trong ngày không, và một phân bổ tĩnh **tốn bao nhiêu** so với phân bổ thay đổi theo giờ. Thống kê phân tán so với null rate hằng = **429,6**. | `tier0_dispersion_ratio = 429.6`. **14/09:** vế thứ hai trả ở **S7**: ngày/đêm theo biên đã đăng ký của phép rút mẫu, giá Fall A1 theo tầng + bootstrap; ở ngân sách trình diễn cặp tốt nhất **chính là điểm tĩnh**, lợi ích `CntTvGain` = 0,0000. Ghi rõ là **mô tả, tính sau khi biết mọi kết quả, không đăng ký**, và giả định sự kiện rải đều trong ngày | **SUPPORTED** |
| **R13** | `[TBD-IV-char-points]` — hàng "Operating points" của bảng characterizability. | 14/09: S13 điền — "Fall only: bảng theo ngân sách trong bài; điểm trình diễn θ = `CntDFivesTheta`, S14". Main `\TBD{IV-char-lambda}` cũng thay bằng `\ref{tab:budget}` | **SUPPORTED** |
| **R14** | `[TBD-IV-char-lambda]` — câu λ đóng mục IV-B. | `theta_vs_lambda.py` | **PENDING-AUTHOR** |
### R6 — cảnh báo bắt buộc (NOTE_LAMBDA_N3 §1)

Câu này `SUPPORTED` **chỉ** như một câu điều kiện. λ-bất biến trên một front một kênh là
**tính chất của N = 1**, không phải kết quả về thiết bị. `theta_vs_lambda.py` trước hôm nay in
"**lambda decides nothing here, and that is itself the finding**" — trái đúng điều NOTE cấm;
đã vá lúc 10:32 (bản lưu `theta_vs_lambda.py.bak_20260910`) và nay in dòng cố định:

> *computed with N = 1 channel in the allocation; λ-invariance on a single-channel front is a
> property of N = 1, not a result about the instrument.*

**Không câu nào trong bản thảo được hàm ý λ không quan trọng** cho tới khi N ≥ 2.

### R8/R9/R12 — hẹp ở đâu, câu thay thế

> **R8:** *Coverage at each registered operating point for the two channels that produced one:
> the fall channel across five thresholds on 78 annotated events, and the smoke/fire channel,
> whose coverage is zero at all five points on 17 annotated fire events (rule-of-three upper
> bound 0.176). The running channel has no row: its checker executed zero times.*
>
> **R9:** *The measured spend–coverage curve for the one channel that has one, each reported
> point a real run at that point, with its reproduction error printed beside it. The remaining
> channels appear in the same table by name, with the reason they carry no curve.*
>
> **R12:** *Alert arrivals are strongly over-dispersed against a constant-rate null (dispersion
> ratio 429.6), so one rate does not describe all hours.* — **Cắt** vế "what a static
> allocation costs against a time-varying one": nó đòi một phân bổ theo giờ mà
> `allocated_theta.json` chưa tồn tại để làm cơ sở.

---

## 5. §V Discussion + §VI — 9 tuyên bố

| # | Tuyên bố | Artefact + SHA | Phán quyết |
|---|---|---|---|
| **D1** | Bảy cơ chế; ba trong bảng `tab:silent`; chúng chia một hình dạng, không phải các lỗi rời rạc. | `silent_mechanisms.csv` `22e3d749b62acd45`; `silent_mechanism_sm{1..7}_{asserted,observed,evidence,issue}` | **SUPPORTED** |
| **D2** | Liên hệ trực tiếp tới phân bổ: kênh chết có FAR hoàn hảo; dedup khác cấu hình dịch mọi rate theo hướng không ai nhìn; lịch sử sự kiện xoá được không dấu vết thì không hậu kiểm được. | SM2, SM3, SM5 + R2 | **SUPPORTED** |
| **D3** | Trên **41/175** segment (**20,3458 h**) cổng chuyển động không mở lần nào; trên **106** segment detector có chạy và không nổ gì. Hai con số là hai sự kiện khác nhau. | `segments_zero_ai_frames=41`, `segments_measured_for_gating=175`, `hours_zero_ai_frames=20.3458`, `segments_zero_alerts=106` | **SUPPORTED** |
| **D4** | "Asked why, the operator gave two reasons at once: false alarms in a residence, and irrelevant functions." | chỉ tồn tại **bên trong** `silent_mechanism_sm2_evidence` ("recorded separately as testimony") | **PARTIAL** |
| **D5** | "The deployment ran with a single detection channel enabled." | `far_deployed_*_alerts`: chỉ Intrusion (11 257) ≠ 0 **trong cửa sổ đo**; nhưng `insitu_alert_types` = `{intrusion: 81848, no_helmet: 4114}` trên chỉ mục alert sống | **PARTIAL** |
| **D6** | Limitations: một site, một camera, một mẫu occupancy — không phải ước lượng quần thể. | thiết kế | **SUPPORTED** |
| **D7** | Limitations: "**Two of the channels entering the allocation** rest on fewer than 20 positive events each, so their curves are drawn with their intervals." | `thin_evidence_channels = RunningChecker, SmokeFireChecker`; `char_in_allocation_n = 1` | **SUPPORTED** |
| **D8** | "The measurement harness built for this work reproduced the same failure it studies, **three times**." | `KNOWN_ISSUES.md` — **24** mục HARNESS-*; không artefact nào chọn ra ba | **SUPPORTED** |
| **S-a** | Bài mang khối tác giả IEEEtran đầy đủ. | — | **PENDING-AUTHOR** |
| **S-b** | Bài mang lời cảm ơn phù hợp nguồn tài trợ và việc dùng AI. | — | **PENDING-AUTHOR** |
| **VI** | `[TBD-conclusion]` | 14/09: `\TBD{concl-d5s}` → `\CntDFivesConclLine{}` (câu "trong/ngoài" sinh theo cờ, không gõ tay). Kèm: đóng góp (c) ở **Intro** nay khớp bản thu hẹp — trước 14/09 Intro vẫn hứa ba phép độ nhạy trong khi C-c đã ghi thu hẹp | **SUPPORTED** |
### D4 / D5 / D8 — câu thay thế

> **D4:** giữ nguyên câu, **thêm** nguồn: cần một file `01_M/OPERATOR_TESTIMONY.md` ghi ngày,
> cách hỏi, và nguyên văn hai lý do, có SHA và vào `LINKS.md`. Chưa có file ấy thì đây là
> lời khai không có bản ghi — điều bài này không cho phép ở bất kỳ chỗ nào khác. **Việc tác
> giả, 15 phút.**
>
> **D5:** *Within the recorded window the deployment raised alerts on one of its seven
> channels. The live alert index shows a second channel that last fired 2026-06-07, before
> the window opened.* — Câu hiện tại đúng cho cửa sổ đo và sai cho lịch sử hệ; 4 114 alert
> `no_helmet` trong chỉ mục làm reviewer bắt được ngay.
>
> **D8:** *Three of the defects in our own harness are of the same family as the ones we
> report on the system under test — a guard asserted and not enforced — and are named, with
> what caught each, in Supplementary Section S5.* Kèm việc: chọn **đích danh** ba mục
> HARNESS-* và ghi vào `analysis/harness_silent_three.csv`, rồi đếm bằng
> `count_everything.py`. Chừng nào chưa có, "three" là chữ gõ tay giữa 24 ứng viên.

### D7 — `UNSUPPORTED`, và **hai lối**

Bảng `tab:characterizability` in `char_in_allocation_n = 1` ở **cùng §IV**. Limitations rồi
nói "hai kênh vào phân bổ". Hai kênh mà `thin_evidence_channels` trỏ tới là Running
(**không có** coverage — checker chạy 0 lần) và SmokeFire (coverage đo được **= 0**); cả hai
**không vào** phân bổ. Kênh duy nhất vào phân bổ là Fall, dựa trên **78** sự kiện — gấp gần
bốn lần ngưỡng 20 mà câu này viện.

> **Lối (a) — cắt.** Bỏ câu; thay bằng câu về đúng cái đang mỏng:
> *The one channel that enters the allocation rests on 78 annotated events; the two channels
> that do not enter rest on 16 and 17, which is part of why they do not.*
> **Giá:** 0 trang. Mất một câu tự-phê vốn đang sai đối tượng.
>
> **Lối (b) — hạ cấp thành observation ở §IV-B.** Chuyển "thin evidence" thành một cột của
> bảng characterizability (số sự kiện có chú thích mỗi kênh: 78 / 17 / 16), rồi Limitations
> chỉ trỏ sang.
> **Giá:** +1 cột bảng ≈ 0,04 trang; **được** một con số mà reviewer sẽ hỏi và hiện chưa có
> trên trang.
>
> **Nguyên nhân gốc, phải sửa dù chọn lối nào:** `count_everything.py` tính
> `thin_evidence_channels` **không** giao với `char_*_allocation == "yes"`. Thêm assert đó
> thì `count_everything.py` sẽ tự bắt mâu thuẫn này lần sau.

---

## 6. Đối chiếu ngược — bằng chứng đã đo mà **không tuyên bố nào dùng**

`render_check` hôm nay: **86 printed of 317 defined counts**. **231 đại lượng đã đếm không
bao giờ lên trang.** Phần lớn là hợp lệ (macro phụ trợ). Chín khối dưới đây thì không:

| # | Artefact đã đo | SHA | Vì sao lãng phí |
|---|---|---|---|
| **1** | **Cổng tái tạo C2** — 50 hàng, 24 segment × 3 checker, `real/replay/exact/extra/missing/max_dt` | `03b1859048cd555b` | Không một macro `\Cnt*` nào; không bảng; chỉ được trỏ bằng `[TBD-IV-C-repro-table]`. Đây là *phép đo về chính thiết bị đo của ta* mà §III hứa "published beside the curve rather than summarised" — và nó đang không được publish ở đâu cả. **Đây cũng là artefact phản bác P7.** |
| **2** | **`theta_transport` / stateful divergence của Fall** — replay thu hồi **0/185** alert | trong (1) | Kết quả mạnh nhất về giới hạn của record-then-rescore; hiện không có một chữ số nào trên trang. |
| **3** | **Layer-1 detector metrics** — 4 checker × 2 split trên COCO val2017 (`mAP50` 0,5410 full / 0,5761 seed500; person AP50 0,7207) | `a76e61a2f78de678` (Intrusion full) + 7 file nữa | Chỉ được trỏ bằng `[TBD-S6]`. Không macro. Đây là bằng chứng duy nhất tách "detector kém" khỏi "checker kém" — đúng câu hỏi reviewer sẽ hỏi về coverage = 0 của SmokeFire. |
| **4** | **Dải ρ = (0,080 · 0,494 · 0,568)** — OmniFall Table 2 degradation | `0ae1072b1b504dbb` | "A declared uncertainty band" là **nửa của đóng góp (b)**, và **không một giá trị ρ nào có trên trang in**. |
| **5** | **Bảng characterizability đầy đủ** — `char_*_reason` (câu dài) vs `char_*_reason_short` | trong `generated_counts.json` | Bảng in nhãn ngắn; bốn câu lý do đầy đủ nằm trong `char_blocked_reasons` và **chưa** xuất hiện thành văn xuôi cạnh bảng như đã dự định 09/09. |
| **6** | **So sánh hai FOV** — `fov_segments.csv`, 175 hàng, job S0 | `6f462149f776806d` | §III hứa "hours are reported per view"; **không có** con số per-view nào trên trang. |
| **7** | **Chỉ mục alert sống** — 85 962 hàng, `{intrusion: 81848, no_helmet: 4114}` | `live_alert_index_20260902.csv` | Chỉ dùng để suy ra deployed rate. 4 114 alert helmet lịch sử là bằng chứng trực tiếp cho SM2 và không được nhắc. |
| **8** | **Sàn lặp lại** — `NOISE_FLOOR_cell0.json`, 160 clip / 612 alert / 0 divergent | — | Được **nói** ba lần (abstract, §I, §III.D) và **đếm** 0 lần. Xem A5. |
| **9** | **X0 / X0a / X0b, PARITY_{A1,P1,TIME,ALERTSENT}, DIAG1/2, `dedup`, `opverify`, `pan`, `qc`, EQ_REAL/EQF_REAL** | `J:out/` | Đã chạy, có output, không tuyên bố nào viện. Một số là chẩn đoán nội bộ (hợp lệ); `PARITY_*` và `EQ_REAL` thì **không** — chúng là bằng chứng in-situ về determinism mà A5 đang thiếu. |

**Khuyến nghị rẻ nhất, xếp theo lợi/công:**
(1) thêm `count_noise_floor()` + `count_reproduction_gate()` vào `count_everything.py` — mở
khoá A5, C-a, P7, R10 cùng lúc, ≈ 45 phút harness;
(2) một cột "annotated events" vào bảng characterizability — sửa D7 và trả lời trước một câu
hỏi chắc chắn bị hỏi, ≈ 0,04 trang;
(3) một dòng ρ vào §III.D — cứu nửa đóng góp (b), ≈ 2 dòng.

---

## 7. Câu phải nói đúng ở dòng đóng góp (c)

Theo luật 5. Trên bằng chứng ngày 10/09/2026:

> **Bài này hiện chứng minh phân bổ trên MỘT kênh.** Fall là kênh duy nhất có cả trục giá
> (FAR in-situ, native, ba điểm thật) và trục lợi (coverage ex-situ, khoảng Wilson). Mệnh đề 1
> và 2 được kiểm trên ba điểm ấy. **Mệnh đề 3 chưa được kiểm nghiệm trên dữ liệu**: ở N = 1 nó
> suy biến về Mệnh đề 1. Hai trong ba phép độ nhạy đã đăng ký không chạy được, và lý do là
> tính chất đo được của thiết bị chứ không phải thiếu thời gian máy.

Bất kỳ câu nào trong bản thảo mờ hơn thế là tô hồng.

---

*Sổ này được đối chiếu lại mỗi lần `count_everything.py` đổi số hoặc một job đổi trạng thái.
Lần đối chiếu kế tiếp: khi X3b + SFCTL trả kết quả, hoặc khi gói 100 nhãn về — cái nào trước.*

---


<!-- LEDGER:END -->

---

# SOÁT NGƯỢC 10/09 tối — **0 dòng đỏ là lúc phải nghi, không phải lúc mừng**

Một ngày mà hai kênh rời phân bổ và một tuyên bố bị vô hiệu, mà sổ kết thúc
không còn dòng `UNSUPPORTED` nào, là một kết quả **đáng ngờ về mặt cấu trúc**.
Dưới đây là **mọi dòng đổi phán quyết hôm nay**, bốn cột, áp luật phân biệt:

> **Hợp lệ** = câu chữ **thu hẹp đúng bằng** bằng chứng. **Không hợp lệ** = câu
> chữ được **nới/làm mờ** cho vừa bằng chứng, **hoặc** phán quyết đổi màu mà câu
> chữ **không đổi** — cùng một tuyên bố không thể tự nhiên được đỡ tốt hơn.

| # | câu chữ **cũ** | cũ | câu chữ **mới** | mới | phán xử |
|---|---|---|---|---|---|
| **C-c** | *"…sensitivity to the interval width, to the two thinnest coverage curves moving together, and to the inclusion or exclusion of the channel that consumes most of the budget."* | `UNSUPPORTED` | *"An allocation procedure … **and the evidence a deployment must supply before it can be run** … we report which of the registered sensitivity analyses the resulting evidence can and cannot support, **and why**."* | `SUPPORTED` | **HỢP LỆ.** Phạm vi **nhỏ đi**: bỏ hẳn hai phép độ nhạy được hứa, thêm một tuyên bố đã đo xong (1/7 kênh). Không có gì được tuyên bố thêm. |
| **P7** | *"on one segment the two streams matched exactly in count and differed on **a fifth of the timestamps by one to five seconds**"* | `UNSUPPORTED` | *"the replay recovered **0 of the 185** fall alerts … every alert it did match fell within **0.010 s**"* — sinh từ macro | `SUPPORTED` | **HỢP LỆ.** Câu cũ **sai sự thật**; câu mới là con số artefact, mạnh hơn và hẹp hơn. Đây là **sửa lỗi**, không phải nới. |
| **D7** | *"**Two of the channels entering the allocation** rest on fewer than twenty positive events each"* | `UNSUPPORTED` | *"the one channel that enters the allocation rests on 78 annotated events; the two that do not rest on 16 and 17"* — sinh từ macro | `SUPPORTED` | **HỢP LỆ.** Câu cũ sai; câu mới đúng và **bất lợi hơn** (nói rõ chỉ một kênh). |
| **P10** | *"**Part of the annotation used a machine-assisted proposal step** with human adjudication. The override rate is reported in S6."* | `PENDING-AUTHOR` | *"A machine-assisted proposal step … **was not used**. Every label … by the author directly, in a single pass … The override rate is therefore **not applicable**."* | `SUPPORTED` | **HỢP LỆ.** Câu cũ sai sự thật; câu mới **thu hẹp tối đa** — từ "đã dùng một quy trình" xuống "đã thiết kế và không dùng". |
| **TBD-labels** | `[TBD-labels]`, chưa có câu | `PENDING-AUTHOR` | *"…false-alarm fraction is 0.0000 [0, 0.0370] … at most 6.2455/h"* + *"a channel can exhaust an operator's attention while being right every time"* | `SUPPORTED` | **HỢP LỆ.** Placeholder → số đo được, kèm cận trên và **kèm giới hạn** (chuyển cửa sổ, dân số không tái tạo được). |
| **A5 / C-a / P6** | *"A measured repeatability floor of **zero** … so every difference reported is a property of the input"* | `PARTIAL` | cùng câu + `\CntNoiseFloorLine{}` **và** `\CntNoiseFloorLimit{}`: *"ex-situ replay path only; no in-situ segment was run twice, and the two channels that raised no alert contribute no evidence"* | `SUPPORTED` | **HỢP LỆ.** Câu gốc giữ nguyên nhưng **kèm giới hạn in ra**; phạm vi hiệu dụng nhỏ đi. |
| **D8** | *"the measurement harness … reproduced the same failure it studies, **three times**"* | `PARTIAL` | *"**seven** such mechanisms … five of them found on a single day … **a rate of detection, which is not the same quantity as a rate of occurrence**"* | `SUPPORTED` | **HỢP LỆ, nhưng đây là dòng duy nhất mà con số TĂNG.** Nó hợp lệ vì (i) mỗi dòng có artefact trong `harness_silent.csv`, (ii) câu mới **tự hạ giá chính nó** bằng mệnh đề detection-vs-occurrence, tức không tuyên bố nhiều hơn dữ liệu chịu được. |
| **R8** | *"coverage per channel at each operating point"* | `SUPPORTED` một nửa | Fall xong; SmokeFire **rút khỏi cột coverage**; Running **chưa chấm** | **`PARTIAL`** | **ĐI NGƯỢC** — dòng này **xấu đi** hôm nay. Ghi để thấy soát không chỉ một chiều. |

## Phán xử tổng

**Không dòng nào rơi vào nhóm hai.** Không dòng nào đổi màu mà câu chữ giữ
nguyên: sáu dòng đổi câu, và trong đó **ba dòng (P7, D7, P10) là sửa một câu
SAI**, hai dòng (C-c, A5) là **thu hẹp**, một dòng (TBD-labels) là điền số đo
được. Một dòng (**R8**) đi ngược.

**Vì sao 0 `UNSUPPORTED` là kết quả thật, không phải chiều:** ba dòng đỏ của bản
gốc đều đỏ vì **cùng một loại lỗi** — một câu tiếng Anh nói sai về một artefact
đã tồn tại (P7, D7) hoặc về một quy trình chưa từng chạy (C-c hứa ba phép độ
nhạy). Không dòng nào đỏ vì **thiếu phép đo**. Sửa câu chữ **là** cách đúng để
đóng loại lỗi ấy, và nó không mua thêm bằng chứng nào.

**Cái đáng lo còn lại không nằm ở màu**: `PENDING-MACHINE` **5** và `PARTIAL`
**8**. Đó là chỗ bài còn thiếu, và nó không đổi hôm nay.

**Đếm sau soát** (`python audit_ledger.py CLAIM_LEDGER.md`, không gõ tay):
`SUPPORTED` 30 · `PARTIAL` 8 · `PENDING-MACHINE` 5 · `PENDING-AUTHOR` 3 ·
**`UNSUPPORTED` 0** · tổng **46**.

---

# LỊCH SỬ — **SUPERSEDED**, không đọc để biết trạng thái

# REVISION 1 — 10/09/2026 12:05 +07, sau phiên gỡ hàng đợi + thu hồi bằng chứng

Sổ trên là ảnh chụp lúc 10:40. Dưới đây là **những gì đã đổi trong cùng ngày**, và
vì sao. Bản 10:40 **không sửa** — nó là bản ghi của cái đã thấy trước khi sửa.

## Đếm lại

| | 10:40 | **12:05** | đổi vì |
|---|---:|---:|---|
| `SUPPORTED` | 22 | **28** | A5, C-a, P6, R8(một phần), R10, D7 lên hạng |
| `PARTIAL` | 12 | **7** | A5/C-a/P6 (sàn lặp lại) nay có macro và câu đã thu hẹp; R12 vẫn PARTIAL |
| `PENDING-MACHINE` | 5 | **4** | R13 vẫn chờ; A6/R7/R11 chờ `allocated_theta.json` |
| `PENDING-AUTHOR` | 4 | **4** | không đổi |
| `UNSUPPORTED` | **3** | **1** | **P7 và D7 đã sửa**; **C-c còn nguyên** |
| **tổng** | 46 | **44** | R8/R9 gộp một dòng sau khi §IV-B/C có nội dung đo |

`render_check`: **115 printed of 432 defined** (10:40: 86/317). Tỉ lệ 27,1 % →
**26,6 %** — mẫu số tăng nhanh hơn tử số vì bốn bộ đếm mới sinh 115 đại lượng
trong khi bài mới in được 29 cái. **Đó là kết quả đúng, không phải thụt lùi:**
số đại lượng *có thể kiểm chứng được* tăng từ 317 lên 432, và số đại lượng *trên
trang* tăng 86 → 115. Cái đáng lo là 231 → **317** đại lượng chưa dùng, và phần
lớn phần tăng là 30 macro của cổng tái tạo + 40 macro Layer-1, vốn là chi tiết
mà **§S5/§S6 sẽ dùng**, không phải thân bài.

## Dòng đã đổi phán quyết

| # | 10:40 | **12:05** | căn cứ |
|---|---|---|---|
| **P7** | `UNSUPPORTED` — mâu thuẫn artefact | **`SUPPORTED`** | câu sai đã xoá. §III.E nay in `\CntReproGateLine{}` + `\CntReproGateFallRecoveredLine{}`, cả hai sinh từ `analysis/reproduction_gate.csv` `03b18590…`. Con số thật: **replay thu hồi 0/185 alert Fall trên 14 segment**; max Δt **0,010 s**. P9-d nay gác **cả §III**. |
| **D7** | `UNSUPPORTED` — tự mâu thuẫn | **`SUPPORTED`** | `count_thin_evidence()` nay **giao** với `char_*_allocation`, và exit 2 nếu một kênh ứng viên không có phán quyết. Limitations dùng `\CntAllocationEvidenceLine{}`: *"the one channel that enters the allocation rests on 78 annotated events; the two that do not rest on 16 and 17."* |
| **A5 / C-a / P6** | `PARTIAL` — "zero" là chữ gõ tay | **`SUPPORTED`** | `count_noise_floor()` → 14 macro. §III.D nay in `\CntNoiseFloorLine{}` (160 clip, 306 alert mỗi lượt, 0 divergence, predicate in ra) **và** `\CntNoiseFloorLimit{}` — phạm vi hẹp được **in ra**, không giấu: chỉ ex-situ, và hai kênh im lặng không đóng góp bằng chứng. |
| **C-b** | `PARTIAL` — ρ không có trên trang | **`PARTIAL`, hẹp hơn** | ρ nay có: §III.D in `\CntRhoBandLine{}` (0,080 CAUCAFall → 0,568 Le2i, bảy nguồn) + `\CntRhoSweptNotApplied{}` + `\CntRhoCentral{}`/`\CntRhoCentralWhy{}`. **Vẫn PARTIAL** vì vế "rule-of-three" ở §I còn gọi tên sai đại lượng mà bảng IV-A in (Poisson hai phía 0,0439/h). Câu thay thế của bản 10:40 vẫn dùng được, chưa áp. |
| **R10** | `SUPPORTED` (chất liệu) | **`SUPPORTED` (trên trang)** | `tab:repro` vào §IV-C: ba kênh × segments/engine/replay/matched/lost, caption mang max Δt. 10 segment không alert **bị loại khỏi bảng thay vì đếm là đồng ý** — chính là cái mà một con số "12 exact of 24" đã làm. |
| **R8** | `PARTIAL` | **`SUPPORTED` một nửa** | §IV-B nay mang Layer-1: `\CntLayerOneLine{}` + person AP50 và recall của detector dùng chung. Nửa còn lại (bảng coverage 5 θ) vẫn `\TBD`. |
| **C-c** | `UNSUPPORTED` | **`UNSUPPORTED` — KHÔNG ĐỔI** | chờ 14/09. Xem §7 dưới. |

## Ba phát hiện mới trong lúc sửa

1. **HARNESS-26 — dòng tóm tắt của chính nguồn ρ sai.** `OMNIFALL_TABLE2_DEGRADATION.md`
   gọi 0,494 là *median* của bảy giá trị; trung vị thật là **0,164**, và 0,494 là
   **hàng GMDCSA24**. min/max/mean đều đúng. **Không con số phân bổ nào sai** (bài
   quét toàn dải), nhưng cái tên thì sai, và nó đã lan sang `theta_vs_lambda.py`
   (`RHO = (0.080, 0.494, 0.568)  # ... median`). Nay `rho_central` = 0,494 được
   gọi đúng tên — *giá trị của corpus mà bài này thực sự đo coverage trên đó* —
   là **lý do tốt hơn** cái nó đang có. `count_everything.py` in NOTE mỗi lần chạy.
   **Đây là mẫu thứ ba trong một ngày: một dòng tóm tắt mâu thuẫn bảng ngay trên nó.**
2. **P9-d, ngay lần chạy đầu sau khi mở rộng sang §III, bắt ba câu:**
   `Two channels` · `three classes of exclusion` · `two limits`. Cái đầu đã sửa
   bằng cách **gọi tên** (fall và smoke/fire) thay vì đếm. Hai cái sau **cố ý gỡ
   khỏi luật**: chúng là cấu trúc lập luận, không phải đại lượng đo — không
   artefact nào có thể mâu thuẫn chúng.
3. **§IV-E → §IV-D đã trả về đúng chỗ.** Tiểu mục *"Which channels can be
   characterised at all"* thành run-in trong §IV-A (nhãn `sec:iv-char` giữ nguyên,
   không cross-reference nào dịch), nên phân bổ về lại chữ **D** như mọi kế hoạch
   và luật cắt đã đăng ký. §I đóng góp (c) nay trỏ `\ref{sec:iv-d}` thay vì gõ tay `\,D`.

## Đối chiếu ngược — cập nhật

Bốn trong chín khối "lãng phí" đã thu hồi:

| khối | trước | nay |
|---|---|---|
| **1. cổng tái tạo C2** | 0 macro, 0 bảng | **30 macro**, bảng `tab:repro` ở §IV-C, nguồn 19/21 của `LINKS.md` |
| **2. `theta_transport`** | không một chữ số trên trang | `\CntThetaTransportLine{}` ở §IV-C; **0/185** ở §III.E |
| **3. Layer-1** | 0 macro | **40 macro**, một đoạn ở §IV-B |
| **4. dải ρ** | 0 giá trị trên trang | **13 macro**, một đoạn ở §III.D, nguồn 21/21 |
| 5–9 (bảng characterizability đầy đủ · hai FOV · chỉ mục alert sống · sàn lặp lại · PARITY/EQ_REAL) | — | **5. sàn lặp lại ĐÃ thu hồi** (14 macro). Bốn khối còn lại **chưa**. |

**Còn lãng phí, xếp theo giá trị:** so sánh hai FOV (§III hứa "hours are reported
per view", **vẫn không có con số per-view nào**) · 4 114 alert `no_helmet` lịch
sử trong chỉ mục sống, bằng chứng trực tiếp cho SM2 · `PARITY_*` và `EQ_REAL`,
là bằng chứng **in-situ** về determinism mà `\CntNoiseFloorLimit{}` đang phải
thừa nhận là thiếu.

## Điều KHÔNG đổi

**Đóng góp (c) vẫn `UNSUPPORTED`, và bài vẫn chỉ chứng minh phân bổ trên một
kênh.** Không một dòng nào của §IV.D được viết. `allocated_theta.json` chưa tồn
tại. Hai bản của đoạn (c) vẫn nằm chờ trong `../00_Plan/AUTHOR_DECISIONS_1009.md`,
nay kèm **bản thu hẹp thứ ba** dùng được ngay ở N = 1.

**Một thay đổi có thể tới trước 14/09:** X3b đang chạy và
`side_calls_with_boxes` = **14 635** sau 7 clip (X3 có **0** trên 44 801 khung).
Theo E9 §1.4 đó là **nhánh 1**: checker đã thực thi, coverage(θ) là phép đo hợp
lệ **và vào phân bổ kể cả khi lại bằng 0**. Nếu nó giữ tới hết lượt thì
**N = 2**, và ba câu hỏi mà `NOTE_LAMBDA_N3` §2 treo — quét λ thật, độ nhạy cận
dưới, Mệnh đề 3 — **bắt đầu có nội dung**. Sổ này được đối chiếu lại khi X3b xong.

---

# REVISION 2 — 10/09/2026 16:40 +07, **132/132 ô nhãn đã về**

Ba gói được **khoá SHA256 trước khi đọc một ô nào**
(`GT_protocol/LABEL_PACK_SEAL_20260910.md`, ghi trước lần đọc đầu tiên).
Tác giả điền **trực tiếp, một lượt (P1)**, **không** qua bước đề xuất máy.

| gói | ô | SHA256 |
|---|---:|---|
| Intrusion | 100 | `dea87abb233f3362da467836e6f3fe651cd38a9ddf5c207b0594217fb5ecbb1b` |
| Fall | 12 | `82843c354e518a9cc16afc043e9adbd22cd08a4b17f04060257cf0bb5362d574` |
| Helmet | 20 | `55c1dac3526df28dfa7bf06614a967d5a13b541e29ff0b17095444b2ba70cdb0` |

## Kết quả

**Fall 12/12 `false_alarm` · Helmet 20/20 `false_alarm` · 0 `REAL_EVENT` · 0 `unsure`
ở cả hai.** **Errata E6 KHÔNG kích hoạt.** Tuyên bố âm trọn gói **đứng vững**, và
mọi rate dựng trên nó vẫn là **false-alarm rate**, không phải alert rate. Đây là
kết quả có thể đã đánh sập một nửa bài; nó không đánh sập.

**Intrusion 100 YES · 0 NO · 0 UNSURE** ⇒ FP-fraction **0/100 = 0,0000**,
Wilson 95 % **[0; 0,0370]**, rule of three **0,0300**.
⇒ **FAR Intrusion = 0,0000/h**, cận trên **6,2455/h**
(= cận trên bootstrap của alert rate 168,83 × cận trên Wilson 0,0370);
alert rate triển khai **134,0716/h**, block bootstrap **[101,54; 168,83]**.

**Bootstrap ghép KHÔNG được báo:** mọi lần lấy lại mẫu toàn-YES đều cho
fraction 0, nên tích sập về **[0; 0]** — tạo tác của việc lấy lại mẫu ở biên, và
sẽ là con số sai tự tin nhất trong bài. Khoảng của record là **Wilson × block
bootstrap**. Bản sập vẫn được tính và in ra, có nhãn, vì người đọc có quyền thấy
nó sập. (`scripts/intrusion_far.py`, `analysis/INTRUSION_FAR.json`.)

## Dòng đã đổi phán quyết

| # | trước | **nay** | căn cứ |
|---|---|---|---|
| **R-labels** (`TBD-labels`) | `PENDING-AUTHOR` | **`SUPPORTED`** | placeholder đã tiêu; §IV-A in `\CntIntrusionFarLine{}` + cận trên |
| **P10** (nhãn máy-đề-xuất, override rate ở S6) | `PENDING-AUTHOR` | **`SUPPORTED` sau khi SỬA MỘT CÂU SAI** | §III viết *"Part of the annotation used a machine-assisted proposal step with human adjudication"* — **không đúng**: không ô nào qua bước ấy. Đã viết lại thành *"Who labelled"*: cơ chế được **thiết kế và đăng ký**, rồi **không dùng**; override rate = **không áp dụng**, nói bằng chữ chứ không để trống. |
| **A2** (abstract "false-alarm rates") | `PARTIAL`, hai chỗ hẹp | **`PARTIAL`, còn một** | chỗ hẹp (i) — Intrusion không có FP fraction — **đã giải quyết**. Chỗ hẹp (ii) vẫn còn: hai trong năm kênh đếm 0 alert nên mang giới hạn Poisson, không phải bootstrap. |
| **char Intrusion** | `far=no`, lý do `no_far_denominator` | **`far=yes`**, nguồn `insitu_labelled_fp`, lý do **`no_channel_coverage_curve`** | `char_far_measurable_n` 4 → **5**. **`char_in_allocation_n` vẫn = 1.** |
| **S6** | 🟠 nửa rỗng | 🟢 **nửa nhãn xong** | override rate đã có câu trả lời dứt khoát; nửa metric detector "ở mỗi điểm vận hành" vẫn thiếu |
| **C-c** | `UNSUPPORTED` — Intrusion thiếu mẫu số FAR | **`UNSUPPORTED`, lý do đã đổi** | phép độ nhạy "có/không kênh tiêu phần lớn ngân sách" vẫn không chạy được, nhưng **không còn** vì thiếu FAR — nay vì Intrusion **không có đường coverage ở tầng kênh**: `layer1_coco` là độ chính xác của **detector**, không phải coverage sự kiện intrusion ở lưới θ đã đăng ký. Ghép hai thứ ấy trong một phân bổ là so một detector với một kênh. |

**Đếm lại:** `SUPPORTED` **30** · `PARTIAL` **6** · `PENDING-MACHINE` **4** ·
`PENDING-AUTHOR` **2** · `UNSUPPORTED` **1**. Placeholder trên trang **12 → 11**.

## Một phát hiện mới, và nó lớn hơn con số

FP-fraction **bằng 0** trong khi alert rate là **134/h**. Kênh này **không sai
một lần nào** trong 100 mẫu mù, và vẫn tiêu **93,2 %** ngân sách cảnh báo.

> Vùng intrusion triển khai là **toàn khung hình**, nên một alert vào người
> trong nhà là **dương tính thật về kỹ thuật** và **phiền nhiễu về vận hành**
> cùng lúc. Một kênh có thể vắt kiệt sự chú ý của người vận hành **trong khi
> đúng mọi lần** — một chế độ hỏng mà **không false-alarm rate nào diễn đạt
> được** và **không lượng chính xác nào của detector chữa được**.

Điều này **mạnh hơn** cái bài đang định nói. Trước hôm nay bài ngụ ý Intrusion
chưa định giá được vì thiếu nhãn; nay nó định giá được, và câu trả lời là trục
giá **không phải** false alarm. §IV-A đã viết lại theo hướng đó.

**Quyết định tác giả, chưa quyết:** ngân sách của phân bổ đo bằng **alert** hay
bằng **false alarm**? §I nói *"Every channel that fires consumes the operator's
attention"* — tức **alert**. Nếu vậy Intrusion tốn 134/h bất kể FP-fraction, và
một "ngân sách false-alarm" sẽ **định giá nó bằng 0**. Hai cách đọc cho hai bài
khác nhau, và Mệnh đề 1–3 phát biểu trên trục nào là điều phải chốt **trước khi**
viết §IV.D.

## Còn phụ thuộc nhãn: không còn dòng nào

Mọi dòng từng mang `PENDING-AUTHOR` vì 132 ô nay đã được trả lời. Những gì còn
chặn `allocated_theta.json` **không còn là nhãn**: X3b (**DONE 15:56, 0 alert
RunningChecker ở cả năm θ — nhánh 1 của E9, coverage 0 đo được, chờ chấm**),
SFCTL (**đang chạy từ 15:56:12**), λ, và câu hỏi trục giá ở trên.

---

# REVISION 3 — 10/09/2026 tối. **Số học của chính sổ này sai, và đó là dòng đầu tiên**

## 0. Đối chiếu 43 ↔ 46 — sổ đã mất dòng, im lặng

Tác giả bắt được: 30 + 6 + 4 + 2 + 1 = **43**, không phải 46. Kiểm bằng cách
**đếm từ file** (`audit_ledger.py`, mới, đặt cạnh sổ):

| | tôi đã công bố | **đếm được từ file** |
|---|---|---|
| bản gốc 10:40 | 22 / 12 / 5 / **4** / 3 = **46** | 22 / 12 / 5 / **2** / 3 = **44** |
| Revision 1 | 28 / 7 / 4 / 4 / 1 = 44 | *chưa từng đếm* |
| Revision 2 | 30 / 6 / 4 / 2 / 1 = 43 | *chưa từng đếm* |

**Chẩn đoán, và nó không dễ chịu.** Bản gốc có **44 dòng**, không phải 46. Tôi
đếm `PENDING-AUTHOR` là 4 trong khi bảng chỉ có 2 — vì tôi tính thêm
`author-block` và `acknowledgment`, hai thứ tôi liệt kê **trong văn xuôi §6** và
**chưa bao giờ trở thành dòng có mã**. Chúng có thật, phải làm thật, và **nằm
ngoài sổ**.

Tệ hơn: **không một con số nào trong ba lần công bố được tính từ file**. Cả ba
là chữ tôi gõ. Revision 1 còn viện "R8/R9 gộp một dòng" — **hai dòng ấy vẫn nằm
nguyên trong bảng**, chưa gộp bao giờ.

**Đây là lần thứ năm trong tuần, và là lần đầu tiên trong sổ ghi chép của chính
tôi:** một dòng tóm tắt mâu thuẫn thứ nó tóm tắt (H-26 · P7 · P10 · H-29 · và
đây). Bài có cổng cho macro, cho hình, cho câu phương pháp — và **không có cổng
nào cho cuốn sổ đang kiểm toán bài**.

**Sửa, cùng một cách như mọi lần khác:** `03_Dossier/audit_ledger.py` đếm từ
file. Tiêu đề sổ **không được gõ tay** nữa; chạy nó trước khi công bố bất kỳ
tổng nào. Và hai dòng bị rơi được **thêm vào bảng** dưới đây thay vì sống trong
văn xuôi.

### Hai dòng bổ sung, nay có mã

| # | Tuyên bố | Artefact | Phán quyết |
|---|---|---|---|
| **S-a** | Bài mang khối tác giả IEEEtran đầy đủ (tên, đơn vị, liên hệ, funding nếu có). | — | **PENDING-AUTHOR** |
| **S-b** | Bài mang lời cảm ơn phù hợp với nguồn tài trợ và với việc dùng AI. | — | **PENDING-AUTHOR** |

## 1. N = 1 là **chung cuộc**, và bằng đăng ký chứ không bằng hoàn cảnh

Câu hỏi số 3 của mục 9 — *có cách nào lấy coverage theo lưới θ cho Intrusion ở
mức checker, và tốn bao nhiêu giờ máy?* — có câu trả lời, và nó **không phải một
cái giá**:

> **Không, và lý do đã được đăng ký từ trước.** `PREREGISTERED_M3.md` mang một
> **Registered decision**: *"IntrusionChecker does not enter the allocation"*,
> vì với `monitor_full_frame = true` và không polygon, định nghĩa sự kiện của
> kênh **trùng khít với đầu ra của detector**: *"how often does it catch an
> intrusion" reduces, under this configuration, to "how often does the detector
> see a person"*.

**Zero giờ máy sẽ giúp được.** Đường cong coverage-theo-θ của Intrusion **đã tồn
tại** và **đã đo**: đó chính là Layer-1 person recall theo conf (job X1, DONE,
0,630–0,740 trên lưới conf). Chạy một lượt ex-situ quét conf trên VIRAT sẽ **đo
lại đúng detector ấy** rồi dán nhãn "channel coverage" — chính là phép lẫn lộn
M3 cấm, và nó sẽ tốn ~5 h máy để tạo ra một tuyên bố tệ hơn cái đang có.

*(Thêm: `exsitu/virat/` chỉ có `GT_running_virat.csv`; **không có** chú thích
person-presence. Nên ngay cả nếu muốn làm, mẫu số cũng chưa tồn tại. Nhưng đó là
lý do thứ hai, và lý do thứ nhất đã đủ.)*

**Hệ quả:** giả định của kế hoạch — *"nhãn là đường duy nhất tới N ≥ 2"* — sai
theo cách còn mạnh hơn tác giả nêu. Nhãn cho **FAR**, không cho đường cong; và
với Intrusion **không có đường cong nào để cho**, theo một quyết định đã ký
trước khi có bất kỳ số nào. **N = 1 không phải trạng thái tạm thời đang chờ dữ
liệu. Nó là kết luận.**

## 2. C-c — **đã quyết: bản thu hẹp là bản đăng**

| | |
|---|---|
| trước | `UNSUPPORTED`, ba lối chờ tác giả |
| **nay** | **`SUPPORTED` ở dạng thu hẹp** — bản (c) thu hẹp trong `AUTHOR_DECISIONS_1009.md` là bản sẽ đăng |

Lý do quyết được **ngay bây giờ** thay vì chờ 14/09: điều đang chờ đã xảy ra.
Ba kênh còn lại đã trả lời, mỗi kênh một lý do **đo được**, và không kênh nào
trả lời "chờ thêm dữ liệu". Không còn gì để chờ.

Bản thu hẹp phát biểu (c) là *quy trình phân bổ **và** điều kiện dữ liệu để nó
chạy được*, và nửa thứ hai nay **đã đo xong trên bảy kênh** — mạnh hơn hôm qua,
không yếu hơn.

## 3. Dòng đổi phán quyết trong Revision 3

| # | trước | **nay** | căn cứ |
|---|---|---|---|
| **C-c** | `UNSUPPORTED` | **`SUPPORTED`** (bản thu hẹp) | §1–§2 trên |
| **A4** | `PARTIAL` — coverage "đo" cho ba kênh | **`PARTIAL`, hẹp hơn và khác lý do** | SmokeFire nay **uncharacterised** (E9 §2.4 nhánh 2), không còn là "coverage đo được = 0". Câu thay thế phải nói **hai hạng bằng chứng**, không phải hai con số 0. |
| **R8** | `SUPPORTED` một nửa | **`PARTIAL`** | Fall xong; SmokeFire rút khỏi cột coverage; Running có số 0 đo được **chưa chấm** — `score_exsitu.py` hard-code `FallChecker` và merge gap 30 s, còn VIRAT đăng ký 20 s |
| **D8** ("ba khuyết tật harness cùng họ") | `PARTIAL` | **`SUPPORTED`** | nay có **thừa** ba: H-26 · H-27 · H-29 · H-30 · P7 · P10, tất cả cùng một hình dạng và đều có artefact |
| **S-a**, **S-b** | *không tồn tại trong sổ* | **`PENDING-AUTHOR`** | hai dòng bị rơi, xem §0 |

## 4. Đếm — **tính từ file, không gõ tay**

Chạy `python audit_ledger.py CLAIM_LEDGER.md` để lấy con số hiện hành. Mọi tổng
trong sổ này từ nay phải đến từ lệnh ấy. Tôi không gõ một tổng nào ở đây, vì ba
lần trước tôi gõ và cả ba lần đều sai.
