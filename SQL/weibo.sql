-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Dec 20, 2017 at 04:11 AM
-- Server version: 10.1.16-MariaDB
-- PHP Version: 5.6.24

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `influencer`
--

-- --------------------------------------------------------

--
-- Table structure for table `weibo`
--

CREATE TABLE `weibo` (
  `id` int(11) NOT NULL,
  `product_seg` varchar(32) NOT NULL,
  `circle` varchar(32) NOT NULL,
  `keyword` varchar(64) NOT NULL,
  `keyword_id` int(11) NOT NULL,
  `influencer` varchar(64) NOT NULL,
  `follower` int(11) NOT NULL,
  `share_avg` int(11) NOT NULL,
  `comment_avg` int(11) NOT NULL,
  `share_range` varchar(32) NOT NULL,
  `comment_range` varchar(32) NOT NULL,
  `lastPostTime` datetime NOT NULL,
  `ori_share_avg` int(11) NOT NULL,
  `ori_comment_avg` int(11) NOT NULL,
  `ori_share_range` varchar(32) NOT NULL,
  `ori_comment_range` varchar(32) NOT NULL,
  `ori_lastPostTime` datetime NOT NULL,
  `key_share_avg` int(11) NOT NULL,
  `key_comment_avg` int(11) NOT NULL,
  `key_share_range` varchar(32) NOT NULL,
  `key_comment_range` varchar(32) NOT NULL,
  `key_content` int(11) NOT NULL,
  `post_type` varchar(32) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `link` varchar(128) NOT NULL,
  `article_read` varchar(32) NOT NULL,
  `ratio_content` varchar(32) NOT NULL,
  `official` int(11) NOT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `weibo`
--
ALTER TABLE `weibo`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `weibo`
--
ALTER TABLE `weibo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
