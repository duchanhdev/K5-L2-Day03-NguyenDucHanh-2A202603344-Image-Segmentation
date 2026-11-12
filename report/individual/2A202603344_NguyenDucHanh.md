# Báo cáo thực hành Day 3 — Nguyễn Đức Hạnh

- Mã học viên theo lớp: 2A202603344
- Ngày / CVAT local: 11/11/2026 / CVAT local
- Công cụ đã dùng: CVAT local, Brush để vẽ mask. Không dùng SAM.

## 1. Bài đã nộp

Đã Save và export đủ 14 ảnh. Semantic xuất Segmentation mask 1.1, instance và panoptic xuất COCO 1.0. `python scripts/inspect_submissions.py --dir submissions` báo OK cho cả 9 ZIP (đúng tên ảnh, đúng class, mask dạng RLE với COCO). Chưa chạy scorer, chưa có điểm tự đánh giá.

| Task | File ZIP đúng tên | Hoàn thành mấy ảnh | Điểm tối đa (coach chấm sau) |
| --- | --- | ---: | ---: |
| easy_semantic | easy_semantic.zip | 3 / 3 | 20 |
| medium_instance | medium_instance.zip | 3 / 3 | 32 |
| hard_panoptic | hard_panoptic.zip | 2 / 2 | 30 |
| cp1_holes | cp1_holes.zip | 1 / 1 | 3 |
| cp2_slice | cp2_slice.zip | 1 / 1 | 3 |
| cp5_occlusion | cp5_occlusion.zip | 1 / 1 | 3 |
| cp3_thin | cp3_thin.zip | 1 / 1 | 3 |
| cp4_curb | cp4_curb.zip | 1 / 1 | 3 |
| cp6_coverage | cp6_coverage.zip | 1 / 1 | 3 |
| **Tổng tối đa** | | | **100** |

Ảnh Easy `7ee6d192-89e2408b` chỉ có road, vegetation, sky: khung là cao tốc, không có vỉa hè hay nhà. Xe và dải bê tông bên trái để nền.

Checkpoint đã giữ trong ZIP: `cp1_holes` một mask motorcycle phủ kính gió và vành bánh, chân chống đỏ nằm ngoài xe; `cp2_slice` 11 car và 1 bus là từng mask riêng, hàng xe sát bên phải không gộp; `cp5_occlusion` xe tay ga phía trước là một motorcycle, người lái là person riêng, taxi vàng cắt mép khung vẫn là một car.

## 2. Một quyết định trước khi dùng gợi ý

- Ảnh, vị trí và object Medium đầu tiên tự vẽ: `000000181542.jpg`, phía trên giữa khung, xe bán tải bạc đậu trước cửa hàng. Annotation id 1, bbox khoảng (271, 115, rộng 227, cao 129).
- Class và quy tắc tôi dùng để chọn biên: class `truck`. Biên bám thân xe còn nhìn thấy (cabin, thùng, bánh). Dừng ở chỗ người và xe máy phía trước che khuất. Không lấy bóng trên mặt đường.
- Nếu dùng gợi ý sau đó: không dùng.
- Nếu không dùng gợi ý: không dùng. Người phụ nữ áo dài đứng trước xe là mask `person` riêng. Xe máy cắt ngang góc phải là mask `motorcycle` riêng, không gộp người lái vào xe. Xe bán tải giữ `truck` vì có thùng sau, không gộp vào các `car` đỗ cạnh.

## 3. Một lỗi tôi tìm thấy và sửa

- Task/ảnh/vùng: `hard_panoptic`, ảnh `000000350023.jpg`, sát mép dưới gần giữa, người đang đi xe máy.
- Lỗi thuộc loại: sai lớp / gộp-tách.
- Bằng chứng tôi nhìn thấy: mask đã tô phủ cả người và xe máy bằng màu `person`. COCO của ảnh này có 6 `person` và 0 `motorcycle` (các thing khác trên ảnh vẫn có: 18 car, 1 bus, 1 truck, 4 traffic light, đủ stuff).
- Quy tắc và hành động sửa: person và motorcycle là hai thing. Cần một mask `person` cho người và một mask `motorcycle` cho phần xe còn nhìn thấy. Chưa sửa được trên CVAT trong lần rà file này, nên chưa tách mask.
- Sau sửa đã Save và export lại chưa? Chưa. `hard_panoptic.zip` hiện vẫn gộp xe máy vào person. Không sửa JSON trong ZIP. Cần mở lại job, tách đúng class, Save, export COCO 1.0 rồi thay file ZIP.

Nếu bạn **đã xem Summary tự đánh giá trên GitHub Actions hoặc tự chạy script**, ghi ngắn một kết quả liên quan lỗi vừa sửa: chưa có điểm. Repo không có ground truth nên chưa chạy scorer.

## 4. Ba ca chưa chắc hoặc đã cân nhắc

| Ảnh/vị trí | Hai cách hiểu có thể | Quy tắc/chứng cứ | Quyết định hoặc câu hỏi cho coach |
| --- | --- | --- | --- |
| 1. `cp4_curb`, `7d83710e-4697c3b2`, dải đất và cỏ giữa hai bó vỉa | Gán sidewalk vì nằm ngoài lòng đường. Để nền vì không phải mặt bê tông đi bộ và không phải làn xe. | Task chỉ có road và sidewalk. Lòng đường asphalt đã là road, vỉa bê tông bên phải đã là sidewalk, ranh bám mép bó vỉa. | Để dải đất là nền. Nhờ coach xác nhận nếu dải đất giữa hai vỉa vẫn phải là sidewalk. |
| 2. `cp6_coverage`, `7daa6479-67988f3f`, xe buýt MTA giữa khung và xe tải thùng bên trái | Ép vào car để giảm vùng trống. Để nền vì schema không có bus và truck. | `classes.json` chỉ có road, sidewalk, building, vegetation, sky, car, person. Taxi và ô tô đen đã là car, người bên phải là person, nhà là building. | Bus và truck để nền. Không vẽ mặt đường bị xe che. Hỏi: các lỗ trên vỉa quanh cột nhà có phải building chưa phủ hết không? |
| 3. `cp3_thin`, `839f7736-abe28069`, đầu đèn bên trái và cột đứng đỡ biển Cross Island bên phải | Đầu đèn là traffic sign. Đầu đèn không có trong bốn class nên để nền; chỉ tô biển chữ và cột. | Biển xanh và biển cấm đã là traffic sign. Vài ô nhỏ trên cần đèn bên trái cũng đang là traffic sign. Cột phải của giàn biển hầu như chưa có pole; các cột đèn bên trái đã có pole. | Giữ biển chữ là traffic sign. Hỏi coach có gỡ đầu đèn khỏi traffic sign và tô nốt cột phải bằng brush nhỏ không. |
