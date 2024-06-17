/*
 Navicat Premium Data Transfer

 Source Server         : 毕设pg
 Source Server Type    : PostgreSQL
 Source Server Version : 160001 (160001)
 Source Host           : 192.168.88.132:5432
 Source Catalog        : czq
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 160001 (160001)
 File Encoding         : 65001

 Date: 18/06/2024 00:04:43
*/


-- ----------------------------
-- Sequence structure for chat_msg_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."chat_msg_id_seq";
CREATE SEQUENCE "public"."chat_msg_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for play_record_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."play_record_id_seq";
CREATE SEQUENCE "public"."play_record_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for user_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."user_id_seq";
CREATE SEQUENCE "public"."user_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Table structure for chat_msg
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_msg";
CREATE TABLE "public"."chat_msg" (
  "id" int4 NOT NULL DEFAULT nextval('chat_msg_id_seq'::regclass),
  "user_id" int4,
  "text" varchar(255) COLLATE "pg_catalog"."default",
  "create_time" timestamptz(6)
)
;

-- ----------------------------
-- Records of chat_msg
-- ----------------------------
INSERT INTO "public"."chat_msg" VALUES (16, 2, '12341234', '2024-01-20 21:11:54.942624+00');
INSERT INTO "public"."chat_msg" VALUES (17, 2, '哈哈哈哈哈', '2024-01-20 21:11:59.530557+00');
INSERT INTO "public"."chat_msg" VALUES (18, 3, 'czq', '2024-01-20 21:18:37.047602+00');

-- ----------------------------
-- Table structure for play_record
-- ----------------------------
DROP TABLE IF EXISTS "public"."play_record";
CREATE TABLE "public"."play_record" (
  "id" int4 NOT NULL DEFAULT nextval('play_record_id_seq'::regclass),
  "user_id" int4,
  "role" bool,
  "result" bool,
  "type" int4,
  "create_time" timestamptz(6),
  "rank_diff" int4,
  "coin_diff" int4
)
;
COMMENT ON COLUMN "public"."play_record"."role" IS '地主还是农民';
COMMENT ON COLUMN "public"."play_record"."result" IS '是否胜利';
COMMENT ON COLUMN "public"."play_record"."type" IS '人机、人人或';

-- ----------------------------
-- Records of play_record
-- ----------------------------
INSERT INTO "public"."play_record" VALUES (1, 5, 't', 't', 1, '2024-02-11 04:23:11.599971+00', 60, 200);
INSERT INTO "public"."play_record" VALUES (3, 2, 'f', 'f', 1, '2024-02-11 04:23:11.611984+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (2, 3, 'f', 'f', 1, '2024-02-11 04:23:11.606474+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (5, 2, 'f', 'f', 1, '2024-02-11 03:23:11.611984+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (6, 2, 'f', 'f', 1, '2024-02-11 02:23:11.611984+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (4, 2, 't', 'f', 1, '2024-02-11 01:23:11.611984+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (7, 2, 't', 't', 1, '2024-02-11 01:10:11.611984+00', 30, 100);
INSERT INTO "public"."play_record" VALUES (9, 5, 't', 't', 1, '2024-02-11 05:23:09.20125+00', 60, 200);
INSERT INTO "public"."play_record" VALUES (10, 3, 'f', 'f', 1, '2024-02-11 05:23:09.206289+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (11, 2, 'f', 'f', 1, '2024-02-11 05:23:09.208793+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (12, 3, 't', 't', 1, '2024-03-13 00:49:46.980547+00', 60, 200);
INSERT INTO "public"."play_record" VALUES (13, 5, 'f', 'f', 1, '2024-03-13 00:49:46.986547+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (14, 2, 'f', 'f', 1, '2024-03-13 00:49:46.989052+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (15, 5, 't', 't', 1, '2024-03-13 01:01:18.00322+00', 60, 400);
INSERT INTO "public"."play_record" VALUES (16, 3, 'f', 'f', 1, '2024-03-13 01:01:18.006739+00', -30, -200);
INSERT INTO "public"."play_record" VALUES (17, 2, 'f', 'f', 1, '2024-03-13 01:01:18.010734+00', -30, -200);
INSERT INTO "public"."play_record" VALUES (18, 2, 't', 'f', 1, '2024-03-13 01:08:21.831006+00', -60, -200);
INSERT INTO "public"."play_record" VALUES (19, 3, 'f', 't', 1, '2024-03-13 01:08:21.834005+00', 30, 100);
INSERT INTO "public"."play_record" VALUES (20, 5, 'f', 't', 1, '2024-03-13 01:08:21.836579+00', 30, 100);
INSERT INTO "public"."play_record" VALUES (21, 2, 't', 'f', 1, '2024-03-13 01:09:32.947495+00', -60, -400);
INSERT INTO "public"."play_record" VALUES (22, 3, 'f', 't', 1, '2024-03-13 01:09:32.9506+00', 30, 200);
INSERT INTO "public"."play_record" VALUES (23, 5, 'f', 't', 1, '2024-03-13 01:09:32.954665+00', 30, 200);
INSERT INTO "public"."play_record" VALUES (24, 2, 't', 't', 1, '2024-03-13 01:10:31.493958+00', 60, 200);
INSERT INTO "public"."play_record" VALUES (25, 3, 'f', 'f', 1, '2024-03-13 01:10:31.496947+00', -30, -100);
INSERT INTO "public"."play_record" VALUES (26, 5, 'f', 'f', 1, '2024-03-13 01:10:31.500945+00', -30, -100);

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS "public"."user";
CREATE TABLE "public"."user" (
  "id" int4 NOT NULL DEFAULT nextval('user_id_seq'::regclass),
  "username" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "coin" int4 NOT NULL,
  "rank" int2 NOT NULL,
  "avatar" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "create_time" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO "public"."user" VALUES (3, 'czq', '1234', 1200, 660, 'http://localhost:8000/static/96126bfd-f184-4816-86a1-db54b884b000.png', '2024-01-05 16:20:05.838735+00');
INSERT INTO "public"."user" VALUES (5, 'czq1', '1234', 1900, 950, 'http://localhost:8000/static/b3b5838f-2a4b-4b5a-8e0b-2bd871833923.png', '2024-02-08 23:33:56.25591+00');
INSERT INTO "public"."user" VALUES (2, '陈zq', '1234', 2700, 460, 'http://localhost:8000/static/636d1c8d-ea4e-4d55-af1b-58d798582004.png', '2024-01-05 16:20:05.838735+00');
INSERT INTO "public"."user" VALUES (4, '陈', '1234', 2000, 500, 'http://localhost:8000/static/96126bfd-f184-4816-86a1-db54b884b000.png', '2024-01-05 16:20:05.838735+00');

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."chat_msg_id_seq"
OWNED BY "public"."chat_msg"."id";
SELECT setval('"public"."chat_msg_id_seq"', 18, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."play_record_id_seq"
OWNED BY "public"."play_record"."id";
SELECT setval('"public"."play_record_id_seq"', 26, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."user_id_seq"
OWNED BY "public"."user"."id";
SELECT setval('"public"."user_id_seq"', 5, true);

-- ----------------------------
-- Primary Key structure for table chat_msg
-- ----------------------------
ALTER TABLE "public"."chat_msg" ADD CONSTRAINT "chat_msg_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table play_record
-- ----------------------------
ALTER TABLE "public"."play_record" ADD CONSTRAINT "play_record_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table user
-- ----------------------------
ALTER TABLE "public"."user" ADD CONSTRAINT "user_pkey" PRIMARY KEY ("id");
